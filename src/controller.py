import os
from typing_extensions import TypedDict # 공유되는 상태 구조 정의 **추가 학습 필요
from langgraph.graph import StateGraph, START, END ,MessagesState

from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai.chat_models import ChatGoogleGenerativeAIError
from langchain_codex_oauth import ChatCodexOAuth
from dotenv import load_dotenv
from langgraph.checkpoint.memory import InMemorySaver


# .env 파일 로드
load_dotenv()

@tool
def summarize_tool(text: str) -> str:
    """요약도구"""
    return text[:30] + "..."

@tool
def must_summarize_tool(text: str) -> str:
    """필수 요약도구"""
    return text[:30] + "..."

tools = [summarize_tool,must_summarize_tool]
#LLM모델
gemini_llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    google_api_key=os.getenv("GOOGLE_API_KEY")
).bind_tools([summarize_tool])
codex_llm = ChatCodexOAuth(
    model="gpt-4o",  # ChatGPT 계정에서 지원되는 모델로 변경
    temperature=0.3,
    system_prompt_mode="strict",  # 시스템 프롬프트 drift 방지
)
def agent(state: MessagesState):
    try:
        response = gemini_llm.invoke(state["messages"])
        return {"messages":[response]}
    except ChatGoogleGenerativeAIError as e:
        if "RESOURCE_EXHAUSTED" in str(e):
            print("현재 Gemini API 사용량을 초과했습니다. codex모델로 변경합니다.")
            response = codex_llm.invoke(state["messages"])
            return {"messages":[response]}
        raise

def ask_question(question: str):
    return question

# 그래프를 한 번만 생성 (모듈 레벨) - InMemorySaver가 재사용됨
def _build_graph():
    builder = StateGraph(MessagesState)

    builder.add_node("agent", agent)
    builder.add_node("tools", ToolNode(tools=[summarize_tool]))

    builder.add_edge(START, "agent")

    builder.add_conditional_edges("agent", tools_condition, {
        "tools": "tools",
        "__end__": END
    })
    builder.add_edge("tools", "agent")

    return builder.compile(checkpointer=InMemorySaver())

# 모듈 로드 시 한 번만 실행
compiled_graph = _build_graph()

