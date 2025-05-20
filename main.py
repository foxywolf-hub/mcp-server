#!/usr/bin/env python3

import uvicorn
import ssl
import os
import sys
from pathlib import Path

# 파이썬 패키지 경로 설정
sys.path.append(str(Path(__file__).resolve().parent))

from app.config import settings
from scripts.generate_ssl import generate_self_signed_cert

def main():
    # SSL 인증서 파일 존재 확인 및 생성
    if not os.path.exists(settings.SSL_CERTFILE) or not os.path.exists(settings.SSL_KEYFILE):
        print("SSL 인증서가 없습니다. 새로 생성합니다...")
        cert_dir = os.path.dirname(settings.SSL_CERTFILE)
        if not os.path.exists(cert_dir):
            os.makedirs(cert_dir)
        
        cert_file = os.path.basename(settings.SSL_CERTFILE)
        key_file = os.path.basename(settings.SSL_KEYFILE)
        
        generate_self_signed_cert(cert_dir, cert_file, key_file)
    
    # HTTPS 서버 설정
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain(
        certfile=settings.SSL_CERTFILE,
        keyfile=settings.SSL_KEYFILE
    )
    
    # 서버 실행
    print(f"MCP 서버를 https://localhost:{settings.SERVER_PORT}에서 실행합니다.")
    uvicorn.run(
        "app.main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        ssl=ssl_context,
        reload=settings.DEBUG
    )

if __name__ == "__main__":
    main()
