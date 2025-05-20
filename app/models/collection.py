from sqlalchemy import Column, Integer, String, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.db.base import Base

class ApiTestCollection(Base):
    __tablename__ = "api_test_collection"
    
    collection_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=True)
    
    # 관계 정의
    user = relationship("User", back_populates="collections")
    test_cases = relationship("CollectionTestCase", back_populates="collection")

class CollectionTestCase(Base):
    __tablename__ = "collection_test_case"
    
    collection_id = Column(Integer, ForeignKey("api_test_collection.collection_id"), primary_key=True)
    test_case_id = Column(Integer, ForeignKey("api_test_case.test_case_id"), primary_key=True)
    
    # 관계 정의
    collection = relationship("ApiTestCollection", back_populates="test_cases")
    test_case = relationship("ApiTestCase", back_populates="collections")
