"""Entry point for the FastAPI application.

This file initializes the FastAPI app and includes the API router.
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.web.routers import router as web_router

# Initialize the FastAPI application
app = FastAPI(title="Drone Delivery Server", version="0.0.1", debug=True)

app.mount("/static", StaticFiles(directory="app/web/static"), name="static")
app.include_router(web_router, prefix="")
