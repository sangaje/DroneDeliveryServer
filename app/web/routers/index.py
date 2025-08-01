"""index.py - Main router for the web application.

This module defines the root endpoint for the web application and serves the main index page.

Functions:
- get_index: Handles GET requests to the root endpoint and returns the index page.
"""

from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.services.airsim.config import AirSimConfig
from app.services.airsim.constants import CUSTOM_AIRSIM_CONFIG_KEY, DRONE_GROUP_KEY

router = APIRouter()
templates = Jinja2Templates(directory="app/web/templates")


@router.get("/", response_class=HTMLResponse)
async def get_index(request: Request) -> Any:
    """Root endpoint for the web application.

    Returns a simple message indicating the server is running.
    """
    context = {
        "request": request,
        "airsim_config_names": AirSimConfig().config_names(
            CUSTOM_AIRSIM_CONFIG_KEY
        ),  # List of available AirSim configurations
        "drone_group_config_names": AirSimConfig().config_names(DRONE_GROUP_KEY),
    }
    return templates.TemplateResponse("index.html", context=context)
