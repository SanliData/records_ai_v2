# -*- coding: utf-8 -*-
"""
UPAP Dashboard Router (HTML renderer)
Simplest possible — no heavy frontend.
"""

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

templates = Jinja2Templates(directory="backend/templates")


@router.get("/", response_class=HTMLResponse)
async def show_dashboard(request: Request):
    """
    Render the static UPAP dashboard HTML.
    """
    return templates.TemplateResponse(
        "upap_dashboard.html",
        {
            "request": request
        }
    )
