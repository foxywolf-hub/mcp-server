from typing import Dict, Any, Callable, Awaitable, List, Optional, Type
import json
import logging
from fastapi import WebSocket, WebSocketDisconnect

from app.core.mcp_protocol import mcp_protocol

logger = logging.getLogger(__name__)

class MCPConnectionManager:
    """
    WebSocket 연결 관리
    """
    def __init__(self):
        # 클라이언트 연결 목록
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """
        새 WebSocket 연결 설정
        """
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        """
        WebSocket 연결 해제
        """
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def send_message(self, websocket: WebSocket, message: Dict[str, Any]):
        """
        특정 클라이언트에게 메세지 전송
        """
        await websocket.send_json(message)
    
    async def broadcast(self, message: Dict[str, Any]):
        """
        모든 클라이언트에게 메세지 브로드캩0스트
        """
        for connection in self.active_connections:
            await connection.send_json(message)

class MCPHandler:
    """
    MCP 메세지 처리기
    """
    def __init__(self):
        self.connection_manager = MCPConnectionManager()
        # 작업 핸들러 등록
        self.action_handlers: Dict[str, Callable[[Dict[str, Any], WebSocket], Awaitable[Dict[str, Any]]]] = {}
    
    def register_handler(self, action: str, handler: Callable[[Dict[str, Any], WebSocket], Awaitable[Dict[str, Any]]]):
        """
        작업 핸들러 등록
        
        :param action: 작업 이름
        :param handler: 비동기 핸들러 함수
        """
        self.action_handlers[action] = handler
    
    async def handle_websocket(self, websocket: WebSocket):
        """
        WebSocket 연결 처리
        
        :param websocket: WebSocket 연결
        """
        await self.connection_manager.connect(websocket)
        try:
            while True:
                # 메세지 수신
                raw_message = await websocket.receive_text()
                await self._process_message(raw_message, websocket)
        except WebSocketDisconnect:
            self.connection_manager.disconnect(websocket)
        except Exception as e:
            logger.error(f"WebSocket error: {str(e)}")
            error_message = mcp_protocol.create_error(
                "websocket_error", 
                f"Error processing WebSocket connection: {str(e)}",
                {"traceback": str(e)}
            )
            await self.connection_manager.send_message(websocket, error_message)
            self.connection_manager.disconnect(websocket)
    
    async def _process_message(self, raw_message: str, websocket: WebSocket):
        """
        수신된 메세지 처리
        
        :param raw_message: 원시 메세지
        :param websocket: WebSocket 연결
        """
        try:
            # 메세지 파싱
            message = mcp_protocol.parse_message(raw_message)
            message_type = message.get("message_type")
            content = message.get("content", {})
            
            # 메세지 타입에 따른 처리
            if message_type == "request":
                await self._handle_request(content, websocket)
            elif message_type == "event":
                # 이벤트 처리 (필요 시 구현)
                pass
            else:
                # 지원하지 않는 메세지 타입
                error_message = mcp_protocol.create_error(
                    "unsupported_message_type", 
                    f"Unsupported message type: {message_type}"
                )
                await self.connection_manager.send_message(websocket, error_message)
        except ValueError as e:
            # 메세지 파싱 오류
            error_message = mcp_protocol.create_error(
                "parse_error", 
                f"Error parsing message: {str(e)}"
            )
            await self.connection_manager.send_message(websocket, error_message)
    
    async def _handle_request(self, content: Dict[str, Any], websocket: WebSocket):
        """
        요청 메세지 처리
        
        :param content: 요청 내용
        :param websocket: WebSocket 연결
        """
        action = content.get("action")
        params = content.get("params", {})
        request_id = content.get("request_id", "unknown")
        
        if action in self.action_handlers:
            try:
                # 해당 작업에 대한 핸들러 호출
                result = await self.action_handlers[action](params, websocket)
                # 성공 응답
                response = mcp_protocol.create_response(request_id, "success", result)
                await self.connection_manager.send_message(websocket, response)
            except Exception as e:
                # 실패 응답
                logger.error(f"Error handling request: {str(e)}")
                error_message = mcp_protocol.create_error(
                    "handler_error", 
                    f"Error handling action '{action}': {str(e)}",
                    {"traceback": str(e)}
                )
                await self.connection_manager.send_message(websocket, error_message)
        else:
            # 지원하지 않는 작업
            error_message = mcp_protocol.create_error(
                "unsupported_action", 
                f"Unsupported action: {action}"
            )
            await self.connection_manager.send_message(websocket, error_message)

# 싱글톤 인스턴스
mcp_handler = MCPHandler()
