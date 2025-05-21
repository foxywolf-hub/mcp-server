from fastapi import APIRouter
from app.api.api_v1.endpoints import mcp, postman, test, test_dashboard

api_router = APIRouter()
api_router.include_router(mcp.router, prefix="/mcp", tags=["mcp"])
api_router.include_router(postman.router, prefix="/postman", tags=["postman"])
api_router.include_router(test.router, prefix="/test", tags=["test"])
api_router.include_router(test_dashboard.router, prefix="/test", tags=["test"]) 