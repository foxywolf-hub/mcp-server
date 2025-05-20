from pydantic import BaseModel
from typing import Optional, List

# API 정보 스키마
class ApiInfoBase(BaseModel):
    name: str
    method: str
    endpoint: str
    description: Optional[str] = None

class ApiInfoCreate(ApiInfoBase):
    pass

class ApiInfoUpdate(ApiInfoBase):
    name: Optional[str] = None
    method: Optional[str] = None
    endpoint: Optional[str] = None

class ApiInfoInDB(ApiInfoBase):
    api_id: int
    
    class Config:
        from_attributes = True

# API 테스트 케이스 스키마
class ApiTestCaseBase(BaseModel):
    title: str
    description: Optional[str] = None

class ApiTestCaseCreate(ApiTestCaseBase):
    api_id: int

class ApiTestCaseUpdate(ApiTestCaseBase):
    title: Optional[str] = None
    api_id: Optional[int] = None

class ApiTestCaseInDB(ApiTestCaseBase):
    test_case_id: int
    api_id: int
    
    class Config:
        from_attributes = True

# API 테스트 데이터 스키마
class ApiTestDataBase(BaseModel):
    request_data: str
    expected_response: str

class ApiTestDataCreate(ApiTestDataBase):
    test_case_id: int

class ApiTestDataUpdate(ApiTestDataBase):
    request_data: Optional[str] = None
    expected_response: Optional[str] = None

class ApiTestDataInDB(ApiTestDataBase):
    test_data_id: int
    test_case_id: int
    
    class Config:
        from_attributes = True
