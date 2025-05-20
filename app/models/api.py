from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class ApiInfo(Base):
    __tablename__ = "api_info"
    
    api_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    method = Column(String, nullable=False)
    endpoint = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # 관계 정의
    test_cases = relationship("ApiTestCase", back_populates="api_info", cascade="all, delete-orphan")

class ApiTestCase(Base):
    __tablename__ = "api_test_case"
    
    test_case_id = Column(Integer, primary_key=True, autoincrement=True)
    api_id = Column(Integer, ForeignKey("api_info.api_id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # 관계 정의
    api_info = relationship("ApiInfo", back_populates="test_cases")
    test_data = relationship("ApiTestData", back_populates="test_case", cascade="all, delete-orphan")
    test_runs = relationship("ApiTestRun", back_populates="test_case", cascade="all, delete-orphan")
    collections = relationship("CollectionTestCase", back_populates="test_case")

class ApiTestData(Base):
    __tablename__ = "api_test_data"
    
    test_data_id = Column(Integer, primary_key=True, autoincrement=True)
    test_case_id = Column(Integer, ForeignKey("api_test_case.test_case_id"), nullable=False)
    request_data = Column(Text, nullable=False)
    expected_response = Column(Text, nullable=False)
    
    # 관계 정의
    test_case = relationship("ApiTestCase", back_populates="test_data")
