import os
from functools import lru_cache
from pathlib import Path
from glob import glob
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

@lru_cache(maxsize=1)
def build_chain():
    # 인덱싱
    docs_dir = os.getenv("RAG_DOCS_DIR")
    if not docs_dir:
        raise RuntimeError("RAG_DOCS_DIR 환경변수를 설정하세요.")
    md_paths = sorted(glob(os.path.join(docs_dir, "*.md")))
    md_docs = []
    for p in md_paths:
        md_docs.extend(TextLoader(p, encoding="utf-8").load())
    
    docs = md_docs
    print(f"로딩된 Document 수: {len(docs)}")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
    )
    split_docs = splitter.split_documents(docs)
    print(f"분할된 chunk 수: {len(split_docs)}")

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
    )
    persist_dir = os.getenv(
        "CHROMA_PERSIST_DIR",
        str(Path(__file__).resolve().parent.parent / ".chroma_db"),
    )

    if os.path.exists(persist_dir) and os.listdir(persist_dir):
        vectorstore = Chroma(persist_directory=persist_dir, embedding_function=embeddings)
    else:
        vectorstore = Chroma.from_documents(split_docs, embeddings, persist_directory=persist_dir)

    # RAG
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "다음 문서를 근거로 사용자 질문에 답하세요. "
         "근거가 부족하면 '주어진 자료에서는 확인할 수 없습니다.'라고 답하세요.\n\n"
         "{context}"),
        ("human", "{question}"),
    ])

    llm = build_llm()
    def format_docs(ds):
        return "\n\n".join(d.page_content for d in ds)

    rag = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    return rag

def build_llm():
    provider = os.getenv("LLM_PROVIDER", "google").lower()
    print(f"LLM Provider: {provider}")
    #ollama 수정해서 모델을 변경하여보기
    # if provider == "ollama":
    #     from langchain_ollama import ChatOllama
    #     return ChatOllama(
    #         model=os.getenv("OLLAMA_MODEL", "gemma4:e2b-mlx"),
    #         base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    #     )
    return ChatGoogleGenerativeAI(
        model=os.getenv("GOOGLE_MODEL", "gemini-2.5-flash"),
        google_api_key=os.getenv("GOOGLE_API_KEY"),
    )


def ask_question(question: str) -> str:
    if not question or not question.strip():
        raise ValueError("질문을 입력하세요.")
    chain = build_chain()
    return chain.invoke(question)