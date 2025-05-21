from typing import Dict, Any, Optional, List
import json
import logging
import asyncio
import tempfile
import os
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import newman

from app.models.postman import PostmanCollection, PostmanEnvironment, PostmanTestData
from app.models.test_run import TestRun, TestResult
from app.core.mcp_protocol import mcp_protocol
from app.core.mcp_handler import mcp_handler

logger = logging.getLogger(__name__)

class TestHandler:
    """
    테스트 실행 처리 핸들러
    """
    
    def __init__(self):
        pass
    
    async def run_test(
        self,
        db: AsyncSession,
        collection_id: int,
        environment_id: Optional[int],
        test_data_id: Optional[int],
        user_id: int
    ) -> Dict[str, Any]:
        """
        테스트 실행
        
        :param db: 데이터베이스 세션
        :param collection_id: Collection ID
        :param environment_id: Environment ID (선택)
        :param test_data_id: Test Data ID (선택)
        :param user_id: 사용자 ID
        :return: 테스트 실행 결과
        """
        try:
            # Collection 조회
            collection = await db.get(PostmanCollection, collection_id)
            if not collection:
                return {
                    "status": "error",
                    "message": "Collection not found"
                }
            
            # Environment 조회 (선택)
            environment = None
            if environment_id:
                environment = await db.get(PostmanEnvironment, environment_id)
                if not environment:
                    return {
                        "status": "error",
                        "message": "Environment not found"
                    }
            
            # Test Data 조회 (선택)
            test_data = None
            if test_data_id:
                test_data = await db.get(PostmanTestData, test_data_id)
                if not test_data:
                    return {
                        "status": "error",
                        "message": "Test data not found"
                    }
            
            # 테스트 실행 생성
            test_run = TestRun(
                collection_id=collection_id,
                environment_id=environment_id,
                test_data_id=test_data_id,
                user_id=user_id,
                status="running"
            )
            
            db.add(test_run)
            await db.commit()
            await db.refresh(test_run)
            
            # 테스트 시작 이벤트 전송
            await self._send_test_event("test_started", {
                "test_run_id": test_run.test_run_id,
                "collection_id": collection_id,
                "environment_id": environment_id,
                "test_data_id": test_data_id,
                "user_id": user_id,
                "start_time": test_run.start_time.isoformat()
            })
            
            # 비동기로 테스트 실행
            asyncio.create_task(self._execute_test(db, test_run, collection, environment, test_data))
            
            return {
                "status": "success",
                "message": "Test started",
                "test_run_id": test_run.test_run_id
            }
        except Exception as e:
            logger.error(f"Error running test: {str(e)}")
            return {
                "status": "error",
                "message": f"Error running test: {str(e)}"
            }
    
    async def _execute_test(
        self,
        db: AsyncSession,
        test_run: TestRun,
        collection: PostmanCollection,
        environment: Optional[PostmanEnvironment],
        test_data: Optional[PostmanTestData]
    ):
        """
        테스트 실행 (비동기)
        
        :param db: 데이터베이스 세션
        :param test_run: 테스트 실행 객체
        :param collection: Collection 객체
        :param environment: Environment 객체 (선택)
        :param test_data: Test Data 객체 (선택)
        """
        try:
            # 임시 파일 생성
            with tempfile.TemporaryDirectory() as temp_dir:
                # Collection 파일 저장
                collection_path = os.path.join(temp_dir, "collection.json")
                with open(collection_path, "w") as f:
                    json.dump(collection.collection_data, f)
                
                # Environment 파일 저장 (선택)
                environment_path = None
                if environment:
                    environment_path = os.path.join(temp_dir, "environment.json")
                    with open(environment_path, "w") as f:
                        json.dump(environment.environment_data, f)
                
                # Test Data 파일 저장 (선택)
                test_data_path = None
                if test_data:
                    test_data_path = os.path.join(temp_dir, "test_data.json")
                    with open(test_data_path, "w") as f:
                        json.dump(test_data.test_data, f)
                
                # Newman 실행 옵션 설정
                options = {
                    "collection": collection_path,
                    "environment": environment_path,
                    "data": test_data_path,
                    "reporters": ["cli", "json"],
                    "reporter": {
                        "json": {
                            "export": os.path.join(temp_dir, "report.json")
                        }
                    }
                }
                
                # Newman 실행
                runner = newman.Newman(options)
                
                # 테스트 진행 상황 모니터링
                async def on_test_start(item):
                    await self._send_test_event("test_item_started", {
                        "test_run_id": test_run.test_run_id,
                        "item_name": item.get("name", "Unknown Request"),
                        "start_time": datetime.now().isoformat()
                    })
                
                async def on_test_end(item, result):
                    test_result = TestResult(
                        test_run_id=test_run.test_run_id,
                        request_name=item.get("name", "Unknown Request"),
                        request_url=result.get("request", {}).get("url", {}).get("raw", ""),
                        request_method=result.get("request", {}).get("method", ""),
                        request_headers=result.get("request", {}).get("header", []),
                        request_body=result.get("request", {}).get("body", {}).get("raw", ""),
                        response_status=result.get("response", {}).get("code"),
                        response_headers=result.get("response", {}).get("header", []),
                        response_body=result.get("response", {}).get("body", ""),
                        test_status="passed" if result.get("test", {}).get("status") == "passed" else "failed",
                        test_message=result.get("test", {}).get("message", ""),
                        test_script=result.get("test", {}).get("script", ""),
                        test_script_result=result.get("test", {}).get("result", ""),
                        start_time=datetime.fromtimestamp(result.get("startedAt", 0) / 1000),
                        end_time=datetime.fromtimestamp(result.get("endedAt", 0) / 1000),
                        duration=result.get("endedAt", 0) - result.get("startedAt", 0)
                    )
                    db.add(test_result)
                    await db.commit()
                    
                    await self._send_test_event("test_item_completed", {
                        "test_run_id": test_run.test_run_id,
                        "item_name": item.get("name", "Unknown Request"),
                        "test_status": test_result.test_status,
                        "test_message": test_result.test_message,
                        "duration": test_result.duration,
                        "end_time": test_result.end_time.isoformat()
                    })
                
                runner.on("test_start", on_test_start)
                runner.on("test_end", on_test_end)
                
                summary = await runner.run()
                
                # 결과 처리
                test_run.status = "completed" if summary.get("run", {}).get("failures", []) == [] else "failed"
                test_run.end_time = datetime.now()
                
                # 테스트 결과 통계 업데이트
                run_summary = summary.get("run", {})
                test_run.total_tests = run_summary.get("stats", {}).get("total", 0)
                test_run.passed_tests = run_summary.get("stats", {}).get("assertions", {}).get("total", 0)
                test_run.failed_tests = run_summary.get("stats", {}).get("assertions", {}).get("failed", 0)
                test_run.skipped_tests = run_summary.get("stats", {}).get("assertions", {}).get("skipped", 0)
                
                await db.commit()
                
                # 테스트 완료 이벤트 전송
                await self._send_test_event("test_completed", {
                    "test_run_id": test_run.test_run_id,
                    "status": test_run.status,
                    "total_tests": test_run.total_tests,
                    "passed_tests": test_run.passed_tests,
                    "failed_tests": test_run.failed_tests,
                    "skipped_tests": test_run.skipped_tests,
                    "end_time": test_run.end_time.isoformat()
                })
                
        except Exception as e:
            logger.error(f"Error executing test: {str(e)}")
            test_run.status = "failed"
            test_run.end_time = datetime.now()
            await db.commit()
            
            # 테스트 실패 이벤트 전송
            await self._send_test_event("test_failed", {
                "test_run_id": test_run.test_run_id,
                "error": str(e),
                "end_time": test_run.end_time.isoformat()
            })
    
    async def _send_test_event(self, event_type: str, data: Dict[str, Any]):
        """
        테스트 이벤트 전송
        
        :param event_type: 이벤트 타입
        :param data: 이벤트 데이터
        """
        try:
            event = mcp_protocol.create_event(event_type, data)
            await mcp_handler.connection_manager.broadcast(event)
        except Exception as e:
            logger.error(f"Error sending test event: {str(e)}")
    
    async def get_test_run(
        self,
        db: AsyncSession,
        test_run_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """
        테스트 실행 결과 조회
        
        :param db: 데이터베이스 세션
        :param test_run_id: 테스트 실행 ID
        :param user_id: 사용자 ID
        :return: 테스트 실행 결과
        """
        try:
            # 테스트 실행 조회
            test_run = await db.get(TestRun, test_run_id)
            if not test_run:
                return {
                    "status": "error",
                    "message": "Test run not found"
                }
            
            # 권한 확인
            if test_run.user_id != user_id:
                return {
                    "status": "error",
                    "message": "Not authorized to access this test run"
                }
            
            # 테스트 결과 조회
            query = select(TestResult).where(TestResult.test_run_id == test_run_id)
            result = await db.execute(query)
            test_results = result.scalars().all()
            
            return {
                "status": "success",
                "test_run": {
                    "test_run_id": test_run.test_run_id,
                    "collection_id": test_run.collection_id,
                    "environment_id": test_run.environment_id,
                    "test_data_id": test_run.test_data_id,
                    "status": test_run.status,
                    "start_time": test_run.start_time,
                    "end_time": test_run.end_time,
                    "total_tests": test_run.total_tests,
                    "passed_tests": test_run.passed_tests,
                    "failed_tests": test_run.failed_tests,
                    "skipped_tests": test_run.skipped_tests
                },
                "test_results": [
                    {
                        "test_result_id": tr.test_result_id,
                        "request_name": tr.request_name,
                        "request_url": tr.request_url,
                        "request_method": tr.request_method,
                        "response_status": tr.response_status,
                        "test_status": tr.test_status,
                        "test_message": tr.test_message,
                        "start_time": tr.start_time,
                        "end_time": tr.end_time,
                        "duration": tr.duration
                    }
                    for tr in test_results
                ]
            }
        except Exception as e:
            logger.error(f"Error getting test run: {str(e)}")
            return {
                "status": "error",
                "message": f"Error getting test run: {str(e)}"
            }

# 싱글톤 인스턴스
test_handler = TestHandler() 