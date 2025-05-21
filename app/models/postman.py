from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class PostmanCollection(Base):
    __tablename__ = "postman_collection"
    
    collection_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    collection_data = Column(JSON, nullable=False)  # Postman Collection JSON
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    
    # 관계 정의
    user = relationship("User", back_populates="postman_collections")
    environments = relationship("PostmanEnvironment", back_populates="collection")
    test_data = relationship("PostmanTestData", back_populates="collection")

class PostmanEnvironment(Base):
    __tablename__ = "postman_environment"
    
    environment_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    environment_data = Column(JSON, nullable=False)  # Postman Environment JSON
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    collection_id = Column(Integer, ForeignKey("postman_collection.collection_id"), nullable=False)
    
    # 관계 정의
    collection = relationship("PostmanCollection", back_populates="environments")

class PostmanTestData(Base):
    __tablename__ = "postman_test_data"
    
    test_data_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    test_data = Column(JSON, nullable=False)  # Postman Test Data JSON
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    collection_id = Column(Integer, ForeignKey("postman_collection.collection_id"), nullable=False)
    
    # 관계 정의
    collection = relationship("PostmanCollection", back_populates="test_data") 