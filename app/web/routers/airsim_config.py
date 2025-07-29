"""TODO: Add a description of the module here."""

from typing import Any

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from fastapi.responses import HTMLResponse
router = APIRouter(prefix="/airsim_config")
templates = Jinja2Templates(directory="app/web/templates")


@router.get("/", response_class=HTMLResponse)
async def get_airsim_config(request: Request) -> Any:
    """AirSim configuration endpoint.

    Returns a page with instructions on how to configure AirSim.
    """
    context = {
        "request": request,
    }
    return templates.TemplateResponse("airsim_config.html", context=context)
