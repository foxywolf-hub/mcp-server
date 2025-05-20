from pydantic import BaseModel
from typing import Optional, List

# API 테스트 콜렉션 스키마
class ApiTestCollectionBase(BaseModel):
    name: str
    description: Optional[str] = None

class ApiTestCollectionCreate(ApiTestCollectionBase):
    user_id: Optional[int] = None

class ApiTestCollectionUpdate(ApiTestCollectionBase):
    name: Optional[str] = None
    user_id: Optional[int] = None

class ApiTestCollectionInDB(ApiTestCollectionBase):
    collection_id: int
    user_id: Optional[int] = None
    
    class Config:
        from_attributes = True

# 콜렉션-테스트케이스 연관 스키마
class CollectionTestCaseBase(BaseModel):
    collection_id: int
    test_case_id: int

class CollectionTestCaseCreate(CollectionTestCaseBase):
    pass

class CollectionTestCaseInDB(CollectionTestCaseBase):
    class Config:
        from_attributes = True
