from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src import rag_controller

router = APIRouter(prefix="/rag")


class QuestionRequest(BaseModel):
    question: str
class QueryResponse(BaseModel):
    answer: str

@router.post("")
def aa(payload: QuestionRequest):
    try:
        answer = rag_controller.ask_question(payload.question)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {"answer": answer}
