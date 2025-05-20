from typing import Dict, Any, List, Optional, Union
import json

class MCPProtocol:
    """
    Model Context Protocol (MCP) 구현
    AI Host(Claude, OpenAI, 사용자개발)와의 통신 프로토콜
    """
    
    def __init__(self):
        pass
    
    def format_message(self, message_type: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        MCP 통신을 위한 메세지 형식화
        
        :param message_type: 메세지 타입 (request, response, event, error)
        :param content: 메세지 내용
        :return: 형식화된 MCP 메세지
        """
        return {
            "mcp_version": "1.0",
            "message_type": message_type,
            "content": content,
            "timestamp": self._get_timestamp()
        }
    
    def parse_message(self, raw_message: str) -> Dict[str, Any]:
        """
        수신된 MCP 메세지 파싱
        
        :param raw_message: JSON 문자열 메세지
        :return: 파싱된 메세지
        """
        try:
            message = json.loads(raw_message)
            # 기본 검증
            if "mcp_version" not in message or "message_type" not in message or "content" not in message:
                raise ValueError("Invalid MCP message format")
            return message
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {str(e)}")
    
    def create_request(self, action: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        요청 메세지 생성
        
        :param action: 요청 행동 (예: upload_postman, run_test, get_results)
        :param params: 요청 파라미터
        :return: 요청 메세지
        """
        content = {
            "action": action,
            "params": params or {}
        }
        return self.format_message("request", content)
    
    def create_response(self, request_id: str, status: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        응답 메세지 생성
        
        :param request_id: 요청 ID
        :param status: 상태 (예: success, error)
        :param data: 응답 데이터
        :return: 응답 메세지
        """
        content = {
            "request_id": request_id,
            "status": status,
            "data": data or {}
        }
        return self.format_message("response", content)
    
    def create_event(self, event_type: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        이벤트 메세지 생성
        
        :param event_type: 이벤트 타입 (예: test_started, test_completed)
        :param data: 이벤트 데이터
        :return: 이벤트 메세지
        """
        content = {
            "event_type": event_type,
            "data": data or {}
        }
        return self.format_message("event", content)
    
    def create_error(self, error_code: str, error_message: str, details: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        오류 메세지 생성
        
        :param error_code: 오류 코드
        :param error_message: 오류 메세지
        :param details: 오류 상세 정보
        :return: 오류 메세지
        """
        content = {
            "error_code": error_code,
            "error_message": error_message,
            "details": details or {}
        }
        return self.format_message("error", content)
    
    def _get_timestamp(self) -> int:
        """
        현재 타임스태프 생성
        """
        import time
        return int(time.time())

# 싱글톤 인스턴스
mcp_protocol = MCPProtocol()
