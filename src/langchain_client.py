import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()


def load_system_prompt(path: str | None = None) -> str:
    prompt_path = Path(path or "src/promptTemplate")
    return prompt_path.read_text(encoding="utf-8").strip()


def build_chain():
    system_prompt = load_system_prompt()

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{question}"),
        ]
    )

    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
    )
    parser = StrOutputParser()

    return prompt | model | parser


def ask_question(question: str) -> str:
    if not question or not question.strip():
        raise ValueError("질문을 입력해주세요.")

    if not os.getenv("GOOGLE_API_KEY"):
        raise RuntimeError("GOOGLE_API_KEY가 설정되지 않았습니다.")

    chain = build_chain()
    return chain.invoke({"question": question})


if __name__ == "__main__":
    sample_question = "LangChain에서 프롬프트와 체인이 무엇이 다른지 쉽게 설명해줘."

    try:
        answer = ask_question(sample_question)
        print("질문:", sample_question)
        print("답변:", answer)
    except Exception as error:
        print(f"오류: {error}")