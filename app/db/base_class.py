from typing import Any
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import as_declarative

@as_declarative()
class Base:
    id: Any
    __name__: str
    
    # 테이블 이름을 클래스 이름의 snake_case로 자동 생성
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
