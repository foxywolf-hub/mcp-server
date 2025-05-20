# MCP Server (Model Context Protocol)

## 개요
AI Host(Claude, OpenAI, 사용자개발)에서 범용적으로 사용 가능한 MCP 서버입니다. 사용자가 Postman Collection, Environment, Data json 파일을 업로드하면 테스트 실행 및 관리를 수행합니다.

## 주요 기능
- Postman Collection, Environment, Data json 파일 업로드 및 처리
- 테스트 콜렉션 관리
- API 테스트 케이스 실행 및 결과 관리
- 로컬 HTTPS 서버 (포트 0610)
- Model Context Protocol(MCP) 지원

## 기술 스택
- Python (FastAPI)
- SQLite 데이터베이스
- uv 패키지 관리자
- WebSocket 통신

## 설치 방법

### 전제조건
- Python 3.10 이상
- uv 패키지 관리자

### 설치 단계

1. 레포지토리 복제
   ```bash
   git clone https://github.com/foxywolf-hub/mcp-server.git
   cd mcp-server
   ```

2. uv를 사용하여 의존성 설치
   ```bash
   uv pip install -e .
   ```

3. 환경 변수 설정 (.env 파일 생성)
   ```
   SERVER_HOST=localhost
   SERVER_PORT=610
   DATABASE_URL=sqlite+aiosqlite:///./mcp.db
   SECRET_KEY=your_secret_key_here
   DEBUG=true
   ```

## 실행 방법

### 서버 실행
```bash
python main.py
```

서버가 실행되면 https://localhost:610 주소에서 접속할 수 있습니다.

### API 매뉴얼

API 매뉴얼은 https://localhost:610/docs 에서 확인할 수 있습니다.

## 프로젝트 구조

```
mcp-server/
├── app/                    # 주요 앱 패키지
│   ├── __init__.py
│   ├── main.py             # FastAPI 어플리케이션 엔트리포인트
│   ├── config.py           # 환경 설정
│   ├── api/                 # API 라우터
│   ├── core/                # 주요 기능 모듈
│   ├── crud/                # CRUD 작업 모듈
│   ├── db/                  # 데이터베이스 관련 모듈
│   ├── models/              # SQLAlchemy 모델
│   ├── schemas/             # Pydantic 스키마
│   ├── services/            # 로직 서비스
│   ├── static/              # 정적 파일
│   └── templates/           # Jinja2 템플릿
├── scripts/                # 유틸리티 스크립트
├── certs/                  # SSL 인증서(생성됨)
├── main.py                 # 서버 시작 스크립트
├── pyproject.toml         # 프로젝트 설정
├── requirements.txt       # 의존성 목록
└── README.md              # 이 파일
```

## 기여 방법

1. 레포지토리 포크
2. 기능 개발
3. 풀 리퀘스트 작성

## 라이센스

MIT License
