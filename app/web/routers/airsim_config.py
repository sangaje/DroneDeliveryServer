"""TODO: Add a description of the module here."""

from typing import Any

from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.services.airsim.config import AirSimConfig, AirSimSettings, DroneGroupConfig
from app.services.airsim.constants import (
    CUSTOM_AIRSIM_CONFIG_KEY,
    DRONE_GROUP_KEY,
)

router = APIRouter(prefix="/airsim/config")
templates = Jinja2Templates(directory="app/web/templates")


@router.get("/", response_class=HTMLResponse)
async def get_airsim_config(request: Request, config_name: str = Query("")) -> Any:
    """AirSim configuration endpoint."""
    settings = AirSimSettings(config_name=config_name)
    context = {
        "request": request,
        "config_name": config_name,
        "settings_html": settings.html_form,
    }
    return templates.TemplateResponse("airsim_config.html", context=context)


@router.post("/", response_class=HTMLResponse)
async def post_airsim_config(request: Request) -> Any:
    """Handle AirSim configuration updates."""
    form_data = await request.form()

    settings = AirSimSettings(config_name=str(form_data["config_name"]))

    for key, value in form_data.items():
        if key != "config_name":
            if settings[key] is not None:
                settings[key] = type(settings[key])(value)

    settings.save()
    message = f"Configuration '{settings.name}' saved successfully!"

    return templates.TemplateResponse(
        "index.html",
        context={
            "request": request,
            "airsim_config_name": settings.name,
            "airsim_config_names": AirSimConfig().config_names(CUSTOM_AIRSIM_CONFIG_KEY),
            "drone_group_config_names": AirSimConfig().config_names(DRONE_GROUP_KEY),
            "message": message,
        },
    )


@router.get("/drone_group", response_class=HTMLResponse)
async def get_drone_config(request: Request, config_name: str = Query("")) -> Any:
    """AirSim configuration endpoint."""
    drone_group = DroneGroupConfig(config_name=config_name)
    context = {
        "request": request,
        "config_name": config_name,
        "settings_html": drone_group.html_form,
    }
    return templates.TemplateResponse("drone_group_config.html", context=context)


@router.post("/drone_group", response_class=HTMLResponse)
async def post_drone_config(request: Request) -> Any:
    """Handle AirSim configuration updates."""
    form_data = await request.form()

    drone_group = DroneGroupConfig(config_name=str(form_data["config_name"]))

    for key, value in form_data.items():
        if key != "config_name":
            if drone_group[key] is not None:
                drone_group[key] = type(drone_group[key])(value)

    drone_group.save()
    message = f"Configuration '{drone_group.name}' saved successfully!"

    return templates.TemplateResponse(
        "index.html",
        context={
            "request": request,
            "drone_group_config_name": drone_group.name,
            "drone_group_config_names": AirSimConfig().config_names(DRONE_GROUP_KEY),
            "airsim_config_names": AirSimConfig().config_names(CUSTOM_AIRSIM_CONFIG_KEY),
            "message": message,
        },
    )
