#!/usr/bin/env python3

import os
import sys
from pathlib import Path
from OpenSSL import crypto

def generate_self_signed_cert(cert_dir="./certs", cert_file="cert.pem", key_file="key.pem"):
    # 인증서 저장 디렉토리 생성
    cert_path = Path(cert_dir)
    cert_path.mkdir(exist_ok=True)
    
    # 개인키 생성
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 2048)
    
    # 인증서 생성
    cert = crypto.X509()
    cert.get_subject().C = "KR"  # 국가
    cert.get_subject().ST = "Seoul"  # 지역
    cert.get_subject().L = "Gangnam"  # 도시
    cert.get_subject().O = "MCP Server"  # 조직
    cert.get_subject().OU = "Development"  # 부서
    cert.get_subject().CN = "localhost"  # Common Name
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(365 * 24 * 60 * 60)  # 1년
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(k)
    cert.sign(k, 'sha256')
    
    # 인증서 및 개인키 저장
    with open(cert_path / cert_file, "wb") as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
    
    with open(cert_path / key_file, "wb") as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k))
    
    print(f"Self-signed certificate generated:\n - Certificate: {cert_path / cert_file}\n - Private key: {cert_path / key_file}")

if __name__ == "__main__":
    generate_self_signed_cert()
