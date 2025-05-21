from fastapi import APIRouter
from app.api.api_v1.endpoints import mcp, postman

api_router = APIRouter()
api_router.include_router(mcp.router, prefix="/mcp", tags=["mcp"])
api_router.include_router(postman.router, prefix="/postman", tags=["postman"]) 