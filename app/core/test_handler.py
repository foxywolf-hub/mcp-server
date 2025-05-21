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
                
                # 개별 테스트 결과 저장
                for execution in run_summary.get("executions", []):
                    test_result = TestResult(
                        test_run_id=test_run.test_run_id,
                        request_name=execution.get("item", {}).get("name", "Unknown Request"),
                        request_url=execution.get("request", {}).get("url", {}).get("raw", ""),
                        request_method=execution.get("request", {}).get("method", ""),
                        request_headers=execution.get("request", {}).get("header", []),
                        request_body=execution.get("request", {}).get("body", {}).get("raw", ""),
                        response_status=execution.get("response", {}).get("code"),
                        response_headers=execution.get("response", {}).get("header", []),
                        response_body=execution.get("response", {}).get("body", ""),
                        test_status="passed" if execution.get("test", {}).get("status") == "passed" else "failed",
                        test_message=execution.get("test", {}).get("message", ""),
                        test_script=execution.get("test", {}).get("script", ""),
                        test_script_result=execution.get("test", {}).get("result", ""),
                        start_time=datetime.fromtimestamp(execution.get("startedAt", 0) / 1000),
                        end_time=datetime.fromtimestamp(execution.get("endedAt", 0) / 1000),
                        duration=execution.get("endedAt", 0) - execution.get("startedAt", 0)
                    )
                    db.add(test_result)
                
                await db.commit()
                
        except Exception as e:
            logger.error(f"Error executing test: {str(e)}")
            test_run.status = "failed"
            test_run.end_time = datetime.now()
            await db.commit()
    
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