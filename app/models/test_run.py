from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class TestRun(Base):
    """
    테스트 실행 결과 모델
    """
    __tablename__ = "test_run"
    
    test_run_id = Column(Integer, primary_key=True, autoincrement=True)
    collection_id = Column(Integer, ForeignKey("postman_collection.collection_id"), nullable=False)
    environment_id = Column(Integer, ForeignKey("postman_environment.environment_id"), nullable=True)
    test_data_id = Column(Integer, ForeignKey("postman_test_data.test_data_id"), nullable=True)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    
    status = Column(String, nullable=False)  # running, completed, failed
    start_time = Column(DateTime, default=func.now())
    end_time = Column(DateTime, nullable=True)
    total_tests = Column(Integer, default=0)
    passed_tests = Column(Integer, default=0)
    failed_tests = Column(Integer, default=0)
    skipped_tests = Column(Integer, default=0)
    
    # 관계 정의
    collection = relationship("PostmanCollection", back_populates="test_runs")
    environment = relationship("PostmanEnvironment", back_populates="test_runs")
    test_data = relationship("PostmanTestData", back_populates="test_runs")
    user = relationship("User", back_populates="test_runs")
    test_results = relationship("TestResult", back_populates="test_run", cascade="all, delete-orphan")

class TestResult(Base):
    """
    개별 테스트 결과 모델
    """
    __tablename__ = "test_result"
    
    test_result_id = Column(Integer, primary_key=True, autoincrement=True)
    test_run_id = Column(Integer, ForeignKey("test_run.test_run_id"), nullable=False)
    
    request_name = Column(String, nullable=False)
    request_url = Column(String, nullable=False)
    request_method = Column(String, nullable=False)
    request_headers = Column(JSON, nullable=True)
    request_body = Column(Text, nullable=True)
    
    response_status = Column(Integer, nullable=True)
    response_headers = Column(JSON, nullable=True)
    response_body = Column(Text, nullable=True)
    
    test_status = Column(String, nullable=False)  # passed, failed, skipped
    test_message = Column(Text, nullable=True)
    test_script = Column(Text, nullable=True)
    test_script_result = Column(Text, nullable=True)
    
    start_time = Column(DateTime, default=func.now())
    end_time = Column(DateTime, nullable=True)
    duration = Column(Integer, nullable=True)  # 밀리초 단위
    
    # 관계 정의
    test_run = relationship("TestRun", back_populates="test_results") 