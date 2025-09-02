"""API endpoints for testing purposes."""

from typing import Any
from urllib.parse import quote

from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.services.airsim.config import AirSimConfig, AirSimSettings, DroneGroupConfig
from app.services.airsim.constants import CUSTOM_AIRSIM_CONFIG_KEY, DRONE_GROUP_KEY

router = APIRouter()
templates = Jinja2Templates(directory="app/web/templates")


@router.get("/", response_class=HTMLResponse)
async def get_index(request: Request) -> Any:
    """Root endpoint for the web application."""
    context = {
        "request": request,
        "airsim_config_names": AirSimConfig().config_names(
            CUSTOM_AIRSIM_CONFIG_KEY
        ),  # List of available AirSim configurations
        "drone_group_config_names": AirSimConfig().config_names(DRONE_GROUP_KEY),
    }
    return templates.TemplateResponse("index.html", context=context)


CONFIG_NAME_Q = Query(...)
DRONE_GROUPS_Q = Query(default_factory=list)


@router.get("/download_airsim_settings", response_class=HTMLResponse)
async def download_airsim_settings(
    request: Request,
    config_name: str = CONFIG_NAME_Q,
    drone_groups: list[str] = DRONE_GROUPS_Q,
) -> Any:
    """Download AirSim settings file."""
    airsim_settings = AirSimSettings(config_name=config_name)
    for drone_group in drone_groups:
        airsim_settings.add_drone_group(DroneGroupConfig(drone_group))

    # Implement the logic to download the AirSim settings file
    safe = quote("settings.json", safe="")
    resp = JSONResponse(
        content=airsim_settings.build_settings(),
        media_type="application/json; charset=utf-8",
    )
    resp.headers["Content-Disposition"] = (
        f"attachment; filename=\"{safe}\"; filename*=UTF-8''{safe}"
    )
    resp.headers["Cache-Control"] = "no-store"
    _ = request  # To avoid unused variable warning
    return resp
