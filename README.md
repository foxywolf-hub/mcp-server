# MCP Server (Model Context Protocol)

## 개요
AI Host(Claude, OpenAI, 사용자개발)에서 범용적으로 사용 가능한 MCP 서버입니다. 사용자가 Postman Collection, Environment, Data json 파일을 업로드하면 Redmine에 Create/Update를 수행합니다.

## 주요 기능
- Postman Collection, Environment, Data json 파일 업로드 및 처리
- Redmine 연동 (Create/Update)
- 테스트 실행 및 결과 관리
- 로컬 HTTPS 서버 (포트 0610)

## 기술 스택
- Python (FastAPI)
- SQLite 데이터베이스
- uv 패키지 관리자

## 설치 및 실행 방법
(개발 중)