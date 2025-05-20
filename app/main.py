import ssl
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.db.init_db import init_db

app = FastAPI(
    title="MCP Server",
    description="Model Context Protocol 서버",
    version="0.1.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 배포시 수정 필요
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록 (추후 구현)
# from app.api.api_v1.api import api_router
# app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "MCP Server is running"}

@app.on_event("startup")
async def startup_event():
    await init_db()

if __name__ == "__main__":
    # HTTPS 인증서 설정
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain(
        certfile=settings.SSL_CERTFILE,
        keyfile=settings.SSL_KEYFILE
    )
    
    # 서버 실행
    uvicorn.run(
        "app.main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        ssl=ssl_context,
        reload=settings.DEBUG
    )