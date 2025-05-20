import os
from pydantic_settings import BaseSettings
from pydantic import EmailStr, validator

class Settings(BaseSettings):
    # 기본 설정
    PROJECT_NAME: str = "MCP Server"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True
    
    # 서버 설정
    SERVER_HOST: str = "localhost"
    SERVER_PORT: int = 610
    
    # 데이터베이스 설정
    DATABASE_URL: str = "sqlite+aiosqlite:///./mcp.db"
    
    # 보안 설정
    SECRET_KEY: str = "dev_secret_key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # SSL 인증서 설정
    SSL_CERTFILE: str = "./certs/cert.pem"
    SSL_KEYFILE: str = "./certs/key.pem"
    
    # Redmine 설정
    REDMINE_URL: str = ""
    REDMINE_API_KEY: str = ""
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

settings = Settings()
