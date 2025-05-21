from typing import Dict, Any, Optional
import json
import logging
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.postman import PostmanCollection, PostmanEnvironment, PostmanTestData
from app.core.mcp_protocol import mcp_protocol

logger = logging.getLogger(__name__)

class PostmanHandler:
    """
    Postman 파일 처리 핸들러
    """
    
    def __init__(self):
        pass
    
    async def process_collection(
        self,
        db: AsyncSession,
        collection_data: str,
        name: str,
        description: Optional[str],
        user_id: int
    ) -> Dict[str, Any]:
        """
        Postman Collection 처리
        
        :param db: 데이터베이스 세션
        :param collection_data: Collection JSON 데이터
        :param name: Collection 이름
        :param description: Collection 설명
        :param user_id: 사용자 ID
        :return: 처리 결과
        """
        try:
            # JSON 유효성 검사
            json.loads(collection_data)
            
            # Collection 생성
            collection = PostmanCollection(
                name=name,
                description=description,
                collection_data=collection_data,
                user_id=user_id
            )
            
            db.add(collection)
            await db.commit()
            await db.refresh(collection)
            
            return {
                "status": "success",
                "message": "Collection processed successfully",
                "collection_id": collection.collection_id
            }
        except json.JSONDecodeError:
            return {
                "status": "error",
                "message": "Invalid JSON format"
            }
        except Exception as e:
            logger.error(f"Error processing collection: {str(e)}")
            return {
                "status": "error",
                "message": f"Error processing collection: {str(e)}"
            }
    
    async def process_environment(
        self,
        db: AsyncSession,
        environment_data: str,
        name: str,
        description: Optional[str],
        collection_id: int
    ) -> Dict[str, Any]:
        """
        Postman Environment 처리
        
        :param db: 데이터베이스 세션
        :param environment_data: Environment JSON 데이터
        :param name: Environment 이름
        :param description: Environment 설명
        :param collection_id: Collection ID
        :return: 처리 결과
        """
        try:
            # JSON 유효성 검사
            json.loads(environment_data)
            
            # Environment 생성
            environment = PostmanEnvironment(
                name=name,
                description=description,
                environment_data=environment_data,
                collection_id=collection_id
            )
            
            db.add(environment)
            await db.commit()
            await db.refresh(environment)
            
            return {
                "status": "success",
                "message": "Environment processed successfully",
                "environment_id": environment.environment_id
            }
        except json.JSONDecodeError:
            return {
                "status": "error",
                "message": "Invalid JSON format"
            }
        except Exception as e:
            logger.error(f"Error processing environment: {str(e)}")
            return {
                "status": "error",
                "message": f"Error processing environment: {str(e)}"
            }
    
    async def process_test_data(
        self,
        db: AsyncSession,
        test_data: str,
        name: str,
        description: Optional[str],
        collection_id: int
    ) -> Dict[str, Any]:
        """
        Postman Test Data 처리
        
        :param db: 데이터베이스 세션
        :param test_data: Test Data JSON 데이터
        :param name: Test Data 이름
        :param description: Test Data 설명
        :param collection_id: Collection ID
        :return: 처리 결과
        """
        try:
            # JSON 유효성 검사
            json.loads(test_data)
            
            # Test Data 생성
            test_data_obj = PostmanTestData(
                name=name,
                description=description,
                test_data=test_data,
                collection_id=collection_id
            )
            
            db.add(test_data_obj)
            await db.commit()
            await db.refresh(test_data_obj)
            
            return {
                "status": "success",
                "message": "Test data processed successfully",
                "test_data_id": test_data_obj.test_data_id
            }
        except json.JSONDecodeError:
            return {
                "status": "error",
                "message": "Invalid JSON format"
            }
        except Exception as e:
            logger.error(f"Error processing test data: {str(e)}")
            return {
                "status": "error",
                "message": f"Error processing test data: {str(e)}"
            }

# 싱글톤 인스턴스
postman_handler = PostmanHandler() 