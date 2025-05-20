from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class ApiTestRun(Base):
    __tablename__ = "api_test_run"
    
    test_run_id = Column(Integer, primary_key=True, autoincrement=True)
    test_case_id = Column(Integer, ForeignKey("api_test_case.test_case_id"), nullable=False)
    executed_at = Column(DateTime, default=func.now())
    status = Column(String, nullable=False)
    actual_response = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=True)
    
    # 관계 정의
    test_case = relationship("ApiTestCase", back_populates="test_runs")
    user = relationship("User", back_populates="test_runs")
    results = relationship("ApiTestResult", back_populates="test_run", cascade="all, delete-orphan")

class ApiTestResult(Base):
    __tablename__ = "api_test_result"
    
    result_id = Column(Integer, primary_key=True, autoincrement=True)
    test_run_id = Column(Integer, ForeignKey("api_test_run.test_run_id"), nullable=False)
    assertion = Column(Text, nullable=False)
    passed = Column(Boolean, nullable=False)
    message = Column(Text, nullable=True)
    
    # 관계 정의
    test_run = relationship("ApiTestRun", back_populates="results")
