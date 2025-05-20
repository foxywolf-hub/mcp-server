import json
from typing import Dict, List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.crud_api import api_info, api_test_case, api_test_data
from app.crud.crud_collection import api_test_collection, collection_test_case
from app.schemas.api import ApiInfoCreate, ApiTestCaseCreate, ApiTestDataCreate
from app.schemas.collection import ApiTestCollectionCreate, CollectionTestCaseCreate

class PostmanParser:
    """
    Postman Collection, Environment, Data 파일 파싱 및 저장 서비스
    """
    
    async def parse_and_save(
        self, 
        db: AsyncSession, 
        collection_json: Dict[str, Any],
        environment_json: Optional[Dict[str, Any]] = None,
        data_json: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Postman 파일을 파싱하고 DB에 저장
        """
        # 결과 저장용 객체
        result = {
            "collection_info": {},
            "api_count": 0,
            "test_case_count": 0
        }
        
        # Collection 정보 확인
        collection_info = collection_json.get("info", {})
        collection_name = collection_info.get("name", "Unnamed Collection")
        collection_description = collection_info.get("description", "")
        
        # Collection 객체 생성
        collection_data = ApiTestCollectionCreate(
            name=collection_name,
            description=collection_description,
            user_id=None  # 임시적으로 null, 추후 인증 구현 시 변경
        )
        db_collection = await api_test_collection.create(db, obj_in=collection_data)
        
        result["collection_info"] = {
            "id": db_collection.collection_id,
            "name": db_collection.name,
            "description": db_collection.description
        }
        
        # Collection에서 Item 추출
        items = collection_json.get("item", [])
        await self._process_items(db, items, db_collection.collection_id, result, environment_json, data_json)
        
        return result
    
    async def _process_items(
        self, 
        db: AsyncSession, 
        items: List[Dict[str, Any]], 
        collection_id: int, 
        result: Dict[str, Any],
        environment_json: Optional[Dict[str, Any]] = None,
        data_json: Optional[Dict[str, Any]] = None,
        parent_path: str = ""
    ) -> None:
        """
        Collection의 각 Item 처리
        """
        for item in items:
            # 중첩 폴더인 경우
            if "item" in item and isinstance(item["item"], list):
                folder_name = item.get("name", "")
                new_path = f"{parent_path}/{folder_name}" if parent_path else folder_name
                await self._process_items(db, item["item"], collection_id, result, environment_json, data_json, new_path)
            # API 요청인 경우
            elif "request" in item:
                await self._process_request(db, item, collection_id, result, environment_json, data_json, parent_path)
    
    async def _process_request(
        self, 
        db: AsyncSession, 
        item: Dict[str, Any], 
        collection_id: int, 
        result: Dict[str, Any],
        environment_json: Optional[Dict[str, Any]] = None,
        data_json: Optional[Dict[str, Any]] = None,
        parent_path: str = ""
    ) -> None:
        """
        각 API 요청 처리
        """
        request = item["request"]
        name = item.get("name", "Unnamed Request")
        path_name = f"{parent_path}/{name}" if parent_path else name
        
        # 메서드 추출
        method = request.get("method", "GET")
        
        # URL 추출
        url_data = request.get("url", {})
        url = ""
        
        if isinstance(url_data, str):
            url = url_data
        else:
            # URL 구성 (raw 혹은 구성요소)
            raw_url = url_data.get("raw", "")
            if raw_url:
                url = raw_url
            else:
                # 구성요소로 URL 생성
                host = "." .join(url_data.get("host", []))
                path = "/". join(url_data.get("path", []))
                url = f"{host}/{path}" if host and path else host or path
        
        # API 정보 생성
        api_data = ApiInfoCreate(
            name=path_name,
            method=method,
            endpoint=url,
            description=item.get("description", "")
        )
        db_api = await api_info.create(db, obj_in=api_data)
        result["api_count"] += 1
        
        # 테스트 케이스 생성
        test_case_data = ApiTestCaseCreate(
            api_id=db_api.api_id,
            title=f"Test {name}",
            description=f"Automatically generated test case for {path_name}"
        )
        db_test_case = await api_test_case.create(db, obj_in=test_case_data)
        result["test_case_count"] += 1
        
        # Collection에 테스트 케이스 추가
        await collection_test_case.add_test_case_to_collection(
            db, 
            collection_id=collection_id, 
            test_case_id=db_test_case.test_case_id
        )
        
        # 요청 및 응답 데이터 처리
        request_body = ""
        if "body" in request:
            body_data = request["body"]
            mode = body_data.get("mode", "")
            
            if mode == "raw":
                request_body = body_data.get("raw", "")
            elif mode == "formdata":
                formdata = body_data.get("formdata", [])
                request_body = json.dumps({item.get("key"): item.get("value") for item in formdata})
            elif mode == "urlencoded":
                urlencoded = body_data.get("urlencoded", [])
                request_body = json.dumps({item.get("key"): item.get("value") for item in urlencoded})
        
        # Postman 테스트 응답 추출
        expected_response = ""
        if "response" in item and isinstance(item["response"], list) and len(item["response"]) > 0:
            response = item["response"][0]
            if "body" in response:
                expected_response = response["body"]
        else:
            # 기본 응답
            expected_response = '{"status": "success"}'
        
        # 테스트 데이터 생성
        test_data = ApiTestDataCreate(
            test_case_id=db_test_case.test_case_id,
            request_data=request_body,
            expected_response=expected_response
        )
        await api_test_data.create(db, obj_in=test_data)
