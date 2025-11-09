"""Entry point for the FastAPI application.

This file initializes the FastAPI app and includes the API router.
"""

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware

from app.api import router as api_router
from app.api.v_a0_0_1 import orders
from app.api.v_a0_0_1.index import api_router
from app.services.controller.database import init_db
from app.web.routers import router as web_router

# Initialize the FastAPI application
app = FastAPI(title="Drone Delivery Server", version="0.0.1", debug=True)


class RequestDumpMiddleware(BaseHTTPMiddleware):
    """Middleware to log incoming requests for debugging purposes."""

    async def dispatch(self, request: Request, call_next):
        """Middleware to log incoming requests for debugging purposes."""
        body = await request.body()
        print(
            "REQ %s %s\nHeaders=%s\nBody=%s",
            request.method,
            request.url.path,
            dict(request.headers),
            body.decode(errors="ignore"),
        )
        return await call_next(request)


app.add_middleware(RequestDumpMiddleware)

app.mount("/static", StaticFiles(directory="app/web/static"), name="static")
app.include_router(web_router)
app.include_router(api_router)
app.include_router(orders.router)
app.include_router(api_router, prefix="/api/v_a0_0_1")

init_db()

# if not drone_service.get_all_drones():
#     drone_service.create_drone(
#         drone_id=1,
#         airsim_id="TEST",
#         status="IDLE",
#         max_battery=100.0,
#         cur_battery=100.0,
#         max_payload=5.0,
#         cur_payload=0.0,
#         cur_lat=37.5665,
#         cur_lon=126.9780,
#         cur_alt=10.0,
#     )
