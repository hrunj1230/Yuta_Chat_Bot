from fastapi import FastAPI
from src.rag_router import router as rag_router

app = FastAPI()

app.include_router(rag_router ,tags=["rag"])
