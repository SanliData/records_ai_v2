# -*- coding: utf-8 -*-
"""
UPAP-compatible Dashboard Router
Read-only system overview
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix="/dashboard",
    tags=["dashboard"],
)

templates = Jinja2Templates(directory="backend/templates")


@router.get("", response_class=HTMLResponse)
async def dashboard(request: Request):
    """
    UPAP-aligned dashboard.
    Read-only view, no legacy DB coupling.
    """
    context = {
        "request": request,
        "service_name": "records_ai_v2",
        "mode": "UPAP-only",
        "version": "2.0.0",
        "upap_stages": [
            {"name": "upload", "status": "enabled"},
            {"name": "process", "status": "enabled"},
            {"name": "archive", "status": "locked (v1)"},
        ],
        "legacy_note": "Legacy analytics & upload UIs are disabled. UPAP is the canonical pipeline.",
    }

    return templates.TemplateResponse("dashboard.html", context)
