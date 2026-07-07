from fastapi import APIRouter
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
import src.controller as controller
import uuid

router = APIRouter()

#class
class QueryRequest(BaseModel):
    question: str
    thread_id: str | None = None
class QueryionResponse(BaseModel):
    answer: str
    thread_id: str



#fastAPI
@router.post("/agent")
async def ask_agent(req: QueryRequest):
    # 동일한 그래프 인스턴스 재사용 (InMemorySaver가 대화 기록 유지)
    thread_id = req.thread_id or str(uuid.uuid4())

    # 문자열을 HumanMessage로 변환 (LangGraph 메시지 형식)
    answer = controller.compiled_graph.invoke(
        {"messages": [HumanMessage(content=req.question)]},
        config={"configurable": {"thread_id": thread_id}, "recursion_limit": 10}
    )

    # 디버그 출력
    for line in answer["messages"]:
        print(line)

    # 최종 응답 추출
    final_answer = answer["messages"][-1].content if answer["messages"] else ""
    return QueryionResponse(answer=final_answer, thread_id=thread_id)