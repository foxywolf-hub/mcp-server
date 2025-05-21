#!/usr/bin/env python3

import os
import sys
import sqlite3
import asyncio
from pathlib import Path

# 프로젝트 루트 경로 추가
sys.path.append(str(Path(__file__).parent.parent))

from app.config import settings
from app.db.init_db import async_session

async def clean_database():
    """데이터베이스 테이블 내용 삭제"""
    # 데이터베이스 파일 경로 추출
    db_url = settings.DATABASE_URL
    if db_url.startswith("sqlite"):
        # sqlite+aiosqlite:///./mcp.db 형태에서 경로 추출
        db_path = db_url.split("///")[1]
        # 상대 경로를 절대 경로로 변환
        db_path = os.path.abspath(db_path)
    else:
        print(f"\033[91m지원하지 않는 데이터베이스 URL 형식: {db_url}\033[0m")
        return False
    
    if not os.path.exists(db_path):
        print(f"\033[93m데이터베이스 파일이 존재하지 않습니다: {db_path}\033[0m")
        return False
    
    try:
        # SQLite 연결
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 테이블 목록 가져오기
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        # 외래키 제약조건 끄기
        cursor.execute("PRAGMA foreign_keys = OFF;")
        
        # 테이블 데이터 삭제
        for table in tables:
            table_name = table[0]
            if table_name != "sqlite_sequence" and not table_name.startswith("sqlite_"):
                print(f"\033[94m테이블 데이터 삭제 중: {table_name}\033[0m")
                cursor.execute(f"DELETE FROM {table_name};")
        
        # sqlite_sequence 테이블 초기화 (자동증가 시퀀스 초기화)
        cursor.execute("DELETE FROM sqlite_sequence;")
        
        # 외래키 제약조건 다시 활성화
        cursor.execute("PRAGMA foreign_keys = ON;")
        
        # 변경사항 적용
        conn.commit()
        conn.close()
        
        print("\033[92m데이터베이스 테이블 내용이 성공적으로 삭제되었습니다.\033[0m")
        return True
    except Exception as e:
        print(f"\033[91m데이터베이스 초기화 오류: {e}\033[0m")
        return False

async def main():
    print("\033[93m경고: 이 작업은 데이터베이스의 모든 데이터를 삭제합니다!\033[0m")
    response = input("\033[93m계속하시겠습니까? (y/N): \033[0m")
    
    if response.lower() == "y":
        success = await clean_database()
        if success:
            response_seed = input("\033[93m초기 데이터를 다시 삽입하시겠습니까? (y/N): \033[0m")
            if response_seed.lower() == "y":
                # 초기 데이터 삽입 스크립트 실행
                from scripts.init_test_data import insert_test_data
                await insert_test_data()
        return 0 if success else 1
    else:
        print("\033[94m작업이 취소되었습니다.\033[0m")
        return 0

if __name__ == "__main__":
    asyncio.run(main())
