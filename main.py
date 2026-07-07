from fastapi import FastAPI
from src.router import router as router

app = FastAPI(
    title="YCB v2 API",
    description="LangGraph"
)

# LangGraph 라우터
app.include_router(router)
