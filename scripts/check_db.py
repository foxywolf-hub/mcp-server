#!/usr/bin/env python3

import os
import sys
import sqlite3
from pathlib import Path

# 프로젝트 루트 경로 추가
sys.path.append(str(Path(__file__).parent.parent))

from app.config import settings

def check_database():
    """데이터베이스 상태 확인"""
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
        print("\033[93m데이터베이스를 초기화하려면 'python -m scripts.initialize_db' 명령을 실행하세요.\033[0m")
        return False
    
    try:
        # SQLite 연결
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # 결과를 딧셔너리 형태로 반환
        cursor = conn.cursor()
        
        # 테이블 목록 가져오기
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = cursor.fetchall()
        
        print(f"\033[94m데이터베이스 파일: {db_path}\033[0m")
        print(f"\033[94m테이블 개수: {len(tables)}\033[0m")
        
        # 테이블 레코드 수 확인
        print("\033[94m\n테이블 레코드 현황:\033[0m")
        print("+" + "-" * 30 + "+" + "-" * 12 + "+")
        print("| " + "Table Name".ljust(28) + " | " + "Record Count".ljust(10) + " |")
        print("+" + "-" * 30 + "+" + "-" * 12 + "+")
        
        for table in tables:
            table_name = table["name"]
            cursor.execute(f"SELECT COUNT(*) as count FROM {table_name};")
            count = cursor.fetchone()["count"]
            print(f"| {table_name.ljust(28)} | {str(count).ljust(10)} |")
        
        print("+" + "-" * 30 + "+" + "-" * 12 + "+")
        
        # 외래키 정보 확인
        print("\n\033[94m외래키 현황:\033[0m")
        for table in tables:
            table_name = table["name"]
            cursor.execute(f"PRAGMA foreign_key_list({table_name});")
            foreign_keys = cursor.fetchall()
            
            if foreign_keys:
                print(f"\n테이블 '{table_name}'")
                print("  외래키:")
                for fk in foreign_keys:
                    print(f"    - {fk['from']} -> {fk['table']}.{fk['to']}")
        
        # 데이터베이스 정상성 확인
        cursor.execute("PRAGMA integrity_check;")
        integrity_result = cursor.fetchone()[0]
        
        if integrity_result == "ok":
            print("\n\033[92m데이터베이스 정상성: 양호\033[0m")
        else:
            print(f"\n\033[91m데이터베이스 정상성 문제 발견: {integrity_result}\033[0m")
        
        conn.close()
        return True
    except Exception as e:
        print(f"\033[91m데이터베이스 확인 오류: {e}\033[0m")
        return False

def main():
    success = check_database()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
