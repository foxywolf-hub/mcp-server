from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent.parent.parent / "templates"))

@router.get("/dashboard", response_class=HTMLResponse)
async def test_dashboard(request: Request):
    """
    테스트 대시보드 페이지
    """
    return templates.TemplateResponse("test_dashboard.html", {"request": request}) 