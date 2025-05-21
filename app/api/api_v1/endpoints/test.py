from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api import deps
from app.models.test_run import TestRun, TestResult
from app.models.user import User
from app.core.test_handler import test_handler

router = APIRouter()

@router.post("/run", response_model=dict)
async def run_test(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    collection_id: int,
    environment_id: Optional[int] = None,
    test_data_id: Optional[int] = None,
) -> Any:
    """
    테스트 실행
    """
    try:
        result = await test_handler.run_test(
            db=db,
            collection_id=collection_id,
            environment_id=environment_id,
            test_data_id=test_data_id,
            user_id=current_user.user_id
        )
        
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/runs", response_model=List[dict])
async def list_test_runs(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    사용자의 테스트 실행 목록 조회
    """
    try:
        query = select(TestRun).where(TestRun.user_id == current_user.user_id)
        result = await db.execute(query)
        test_runs = result.scalars().all()
        
        return [
            {
                "test_run_id": tr.test_run_id,
                "collection_id": tr.collection_id,
                "environment_id": tr.environment_id,
                "test_data_id": tr.test_data_id,
                "status": tr.status,
                "start_time": tr.start_time,
                "end_time": tr.end_time,
                "total_tests": tr.total_tests,
                "passed_tests": tr.passed_tests,
                "failed_tests": tr.failed_tests,
                "skipped_tests": tr.skipped_tests
            }
            for tr in test_runs
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/runs/{test_run_id}", response_model=dict)
async def get_test_run(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    test_run_id: int,
) -> Any:
    """
    특정 테스트 실행 결과 조회
    """
    try:
        result = await test_handler.get_test_run(
            db=db,
            test_run_id=test_run_id,
            user_id=current_user.user_id
        )
        
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 