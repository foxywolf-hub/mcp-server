from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# API 테스트 실행 스키마
class ApiTestRunBase(BaseModel):
    test_case_id: int
    status: str
    actual_response: Optional[str] = None

class ApiTestRunCreate(ApiTestRunBase):
    user_id: Optional[int] = None

class ApiTestRunUpdate(ApiTestRunBase):
    status: Optional[str] = None
    actual_response: Optional[str] = None

class ApiTestRunInDB(ApiTestRunBase):
    test_run_id: int
    executed_at: datetime
    user_id: Optional[int] = None
    
    class Config:
        from_attributes = True

# API 테스트 결과 스키마
class ApiTestResultBase(BaseModel):
    assertion: str
    passed: bool
    message: Optional[str] = None

class ApiTestResultCreate(ApiTestResultBase):
    test_run_id: int

class ApiTestResultUpdate(ApiTestResultBase):
    assertion: Optional[str] = None
    passed: Optional[bool] = None

class ApiTestResultInDB(ApiTestResultBase):
    result_id: int
    test_run_id: int
    
    class Config:
        from_attributes = True
