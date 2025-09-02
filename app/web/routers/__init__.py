"""Web API routes for the application.

This module defines the API router and includes all the necessary routes for the application.
"""

import importlib
import pkgutil

from fastapi import APIRouter

router = APIRouter()

# Dynamically import all modules in the current package
# This allows for modular route definitions in separate files
for _, module_name, _ in pkgutil.iter_modules(__path__):  # type: ignore
    module = importlib.import_module(f"{__name__}.{module_name}")
    if hasattr(module, "router"):
        router.include_router(module.router, tags=["Web-" + module_name])
