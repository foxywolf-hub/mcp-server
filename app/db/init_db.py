from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.db.base import Base

# 비동기 엔진 생성
engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)

# 비동기 세션 팩토리 생성
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def init_db():
    """데이터베이스 초기화 함수"""
    try:
        # 비동기 컨텍스트 관리자 사용
        async with engine.begin() as conn:
            # 테이블 생성
            await conn.run_sync(Base.metadata.create_all)
        print("Database initialized successfully")
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise
