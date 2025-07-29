"""
index.py - Main router for the web application.
This module defines the root endpoint for the web application and serves the main index page.

Functions:
- get_index: Handles GET requests to the root endpoint and returns the index page.
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/web/templates")

@router.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    """
    Root endpoint for the web application.
    Returns a simple message indicating the server is running.
    """
    context = {
        "request": request,
    }
    return templates.TemplateResponse("index.html", context=context)