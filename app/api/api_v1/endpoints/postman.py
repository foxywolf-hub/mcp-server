from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api import deps
from app.models.postman import PostmanCollection, PostmanEnvironment, PostmanTestData
from app.models.user import User

router = APIRouter()

@router.post("/collections", response_model=dict)
async def upload_collection(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    name: str = Form(...),
    description: str = Form(None),
    collection_file: UploadFile = File(...),
) -> Any:
    """
    Postman Collection 파일 업로드
    """
    try:
        # 파일 내용 읽기
        content = await collection_file.read()
        collection_data = content.decode()
        
        # Collection 생성
        collection = PostmanCollection(
            name=name,
            description=description,
            collection_data=collection_data,
            user_id=current_user.user_id
        )
        
        db.add(collection)
        await db.commit()
        await db.refresh(collection)
        
        return {
            "message": "Collection uploaded successfully",
            "collection_id": collection.collection_id
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/environments", response_model=dict)
async def upload_environment(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    collection_id: int = Form(...),
    name: str = Form(...),
    description: str = Form(None),
    environment_file: UploadFile = File(...),
) -> Any:
    """
    Postman Environment 파일 업로드
    """
    try:
        # Collection 존재 확인
        collection = await db.get(PostmanCollection, collection_id)
        if not collection:
            raise HTTPException(status_code=404, detail="Collection not found")
        
        # 파일 내용 읽기
        content = await environment_file.read()
        environment_data = content.decode()
        
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
            "message": "Environment uploaded successfully",
            "environment_id": environment.environment_id
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/test-data", response_model=dict)
async def upload_test_data(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    collection_id: int = Form(...),
    name: str = Form(...),
    description: str = Form(None),
    test_data_file: UploadFile = File(...),
) -> Any:
    """
    Postman Test Data 파일 업로드
    """
    try:
        # Collection 존재 확인
        collection = await db.get(PostmanCollection, collection_id)
        if not collection:
            raise HTTPException(status_code=404, detail="Collection not found")
        
        # 파일 내용 읽기
        content = await test_data_file.read()
        test_data = content.decode()
        
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
            "message": "Test data uploaded successfully",
            "test_data_id": test_data_obj.test_data_id
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/collections", response_model=List[dict])
async def list_collections(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    사용자의 Postman Collection 목록 조회
    """
    try:
        query = select(PostmanCollection).where(PostmanCollection.user_id == current_user.user_id)
        result = await db.execute(query)
        collections = result.scalars().all()
        
        return [
            {
                "collection_id": c.collection_id,
                "name": c.name,
                "description": c.description,
                "created_at": c.created_at,
                "updated_at": c.updated_at
            }
            for c in collections
        ]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/collections/{collection_id}", response_model=dict)
async def get_collection(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    collection_id: int,
) -> Any:
    """
    특정 Postman Collection 상세 정보 조회
    """
    try:
        collection = await db.get(PostmanCollection, collection_id)
        if not collection:
            raise HTTPException(status_code=404, detail="Collection not found")
        
        if collection.user_id != current_user.user_id:
            raise HTTPException(status_code=403, detail="Not authorized to access this collection")
        
        return {
            "collection_id": collection.collection_id,
            "name": collection.name,
            "description": collection.description,
            "collection_data": collection.collection_data,
            "created_at": collection.created_at,
            "updated_at": collection.updated_at,
            "environments": [
                {
                    "environment_id": e.environment_id,
                    "name": e.name,
                    "description": e.description
                }
                for e in collection.environments
            ],
            "test_data": [
                {
                    "test_data_id": t.test_data_id,
                    "name": t.name,
                    "description": t.description
                }
                for t in collection.test_data
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 