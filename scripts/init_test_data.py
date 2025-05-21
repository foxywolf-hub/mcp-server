#!/usr/bin/env python3

import os
import sys
import json
import asyncio
import argparse
from pathlib import Path

# 프로젝트 루트 경로 추가
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from app.db.init_db import async_session
from app.models.api import ApiInfo, ApiTestCase, ApiTestData
from app.models.collection import ApiTestCollection, CollectionTestCase
from app.models.user import User

TEST_DATA = {
    "users": [
        {
            "name": "Test User",
            "email": "test@example.com",
            "role": "user"
        },
        {
            "name": "Developer",
            "email": "dev@example.com",
            "role": "developer"
        }
    ],
    "collections": [
        {
            "name": "API Test Collection",
            "description": "Sample API test collection",
            "user_id": 1
        },
        {
            "name": "Integration Tests",
            "description": "Integration testing collection",
            "user_id": 2
        }
    ],
    "apis": [
        {
            "name": "Get All Users",
            "method": "GET",
            "endpoint": "/api/users",
            "description": "Get all users"
        },
        {
            "name": "Get User by ID",
            "method": "GET",
            "endpoint": "/api/users/{id}",
            "description": "Get user by ID"
        },
        {
            "name": "Create User",
            "method": "POST",
            "endpoint": "/api/users",
            "description": "Create a new user"
        },
        {
            "name": "Update User",
            "method": "PUT",
            "endpoint": "/api/users/{id}",
            "description": "Update existing user"
        },
        {
            "name": "Delete User",
            "method": "DELETE",
            "endpoint": "/api/users/{id}",
            "description": "Delete a user"
        }
    ],
    "test_cases": [
        {
            "api_id": 1,
            "title": "Get All Users Test",
            "description": "Test that all users are returned"
        },
        {
            "api_id": 2,
            "title": "Get User By ID Test",
            "description": "Test get user by valid ID"
        },
        {
            "api_id": 2,
            "title": "Invalid User ID Test",
            "description": "Test get user with invalid ID"
        },
        {
            "api_id": 3,
            "title": "Create User Test",
            "description": "Test creating a new user"
        },
        {
            "api_id": 4,
            "title": "Update User Test",
            "description": "Test updating existing user"
        },
        {
            "api_id": 5,
            "title": "Delete User Test",
            "description": "Test deleting a user"
        }
    ],
    "collection_test_cases": [
        {"collection_id": 1, "test_case_id": 1},
        {"collection_id": 1, "test_case_id": 2},
        {"collection_id": 1, "test_case_id": 3},
        {"collection_id": 2, "test_case_id": 3},
        {"collection_id": 2, "test_case_id": 4},
        {"collection_id": 2, "test_case_id": 5},
        {"collection_id": 2, "test_case_id": 6}
    ],
    "test_data": [
        {
            "test_case_id": 1,
            "request_data": "{}",
            "expected_response": "{\"users\": [{\"id\": 1, \"name\": \"Test User\"}, {\"id\": 2, \"name\": \"Developer\"}]}"
        },
        {
            "test_case_id": 2,
            "request_data": "{\"id\": 1}",
            "expected_response": "{\"id\": 1, \"name\": \"Test User\", \"email\": \"test@example.com\", \"role\": \"user\"}"
        },
        {
            "test_case_id": 3,
            "request_data": "{\"id\": 999}",
            "expected_response": "{\"error\": \"User not found\", \"status\": 404}"
        },
        {
            "test_case_id": 4,
            "request_data": "{\"name\": \"New User\", \"email\": \"new@example.com\", \"role\": \"user\"}",
            "expected_response": "{\"id\": 3, \"name\": \"New User\", \"email\": \"new@example.com\", \"role\": \"user\"}"
        },
        {
            "test_case_id": 5,
            "request_data": "{\"id\": 1, \"name\": \"Updated User\", \"email\": \"updated@example.com\", \"role\": \"admin\"}",
            "expected_response": "{\"id\": 1, \"name\": \"Updated User\", \"email\": \"updated@example.com\", \"role\": \"admin\"}"
        },
        {
            "test_case_id": 6,
            "request_data": "{\"id\": 2}",
            "expected_response": "{\"success\": true, \"message\": \"User deleted successfully\"}"
        }
    ]
}

async def insert_test_data():
    """DB에 테스트 데이터 삽입"""
    print("\033[94m테스트 데이터 삽입 시작...\033[0m")
    
    async with async_session() as db:
        try:
            # 사용자 생성
            for user_data in TEST_DATA["users"]:
                user = User(**user_data)
                db.add(user)
            
            await db.commit()
            print("\033[92m사용자 데이터 삽입 완료\033[0m")
            
            # 콜렉션 생성
            for collection_data in TEST_DATA["collections"]:
                collection = ApiTestCollection(**collection_data)
                db.add(collection)
            
            await db.commit()
            print("\033[92m콜렉션 데이터 삽입 완료\033[0m")
            
            # API 정보 생성
            for api_data in TEST_DATA["apis"]:
                api = ApiInfo(**api_data)
                db.add(api)
            
            await db.commit()
            print("\033[92mAPI 데이터 삽입 완료\033[0m")
            
            # 테스트 케이스 생성
            for test_case_data in TEST_DATA["test_cases"]:
                test_case = ApiTestCase(**test_case_data)
                db.add(test_case)
            
            await db.commit()
            print("\033[92m테스트 케이스 데이터 삽입 완료\033[0m")
            
            # 콜렉션-테스트케이스 연결
            for link_data in TEST_DATA["collection_test_cases"]:
                link = CollectionTestCase(**link_data)
                db.add(link)
            
            await db.commit()
            print("\033[92m콜렉션-테스트케이스 연결 데이터 삽입 완료\033[0m")
            
            # 테스트 데이터 생성
            for data_item in TEST_DATA["test_data"]:
                test_data = ApiTestData(**data_item)
                db.add(test_data)
            
            await db.commit()
            print("\033[92m테스트 데이터 삽입 완료\033[0m")
            
            print("\033[92m모든 테스트 데이터 삽입이 완료되었습니다!\033[0m")
            return True
            
        except Exception as e:
            await db.rollback()
            print(f"\033[91m테스트 데이터 삽입 중 오류 발생: {e}\033[0m")
            return False

async def main():
    parser = argparse.ArgumentParser(description="테스트 데이터 초기화")
    parser.add_argument("--json", type=str, help="사용할 커스텀 JSON 파일 경로 (선택적)")
    args = parser.parse_args()
    
    # 커스텀 JSON 파일이 지정된 경우 로드
    if args.json:
        try:
            with open(args.json, "r", encoding="utf-8") as f:
                custom_data = json.load(f)
                global TEST_DATA
                TEST_DATA = custom_data
                print(f"\033[94m커스텀 JSON 파일 로드 성공: {args.json}\033[0m")
        except Exception as e:
            print(f"\033[91m커스텀 JSON 파일 로드 실패: {e}\033[0m")
            return 1
    
    success = await insert_test_data()
    return 0 if success else 1

if __name__ == "__main__":
    asyncio.run(main())
