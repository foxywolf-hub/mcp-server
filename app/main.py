import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

from app.config import settings
from app.db.init_db import init_db
from app.api.api_v1.api import api_router
from app.api.api_v1.endpoints.ui import router as ui_router

app = FastAPI(
    title="MCP Server",
    description="Model Context Protocol 서버",
    version="0.1.0"
)

# 정적 파일 마운트
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 배포시 수정 필요
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(ui_router)  # UI 라우터

@app.on_event("startup")
async def startup_event():
    await init_db()

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=settings.DEBUG
    )
