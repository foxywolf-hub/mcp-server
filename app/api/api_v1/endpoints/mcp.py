from typing import Any
from fastapi import APIRouter, WebSocket, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.core.mcp_handler import mcp_handler
from app.core.mcp_protocol import mcp_protocol

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    MCP WebSocket 연결 엔드포인트
    """
    await mcp_handler.handle_websocket(websocket)

@router.post("/message")
async def process_message(
    *,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(deps.get_db),
    message: dict,
) -> Any:
    """
    MCP 메세지 처리 (REST API)
    """
    try:
        # 메세지 유형 확인
        message_type = message.get("message_type")
        content = message.get("content", {})
        
        if message_type == "request":
            action = content.get("action")
            params = content.get("params", {})
            request_id = content.get("request_id", "unknown")
            
            # 지원하는 작업인지 확인
            if action in mcp_handler.action_handlers:
                # 비동기 처리를 위해 백그라운드 태스크로 처리
                # (WebSocket대신 REST API로 처리하는 경우에 사용)
                return {
                    "message": f"Processing {action} request",
                    "request_id": request_id,
                    "status": "accepted"
                }
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported action: {action}")
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported message type: {message_type}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")
