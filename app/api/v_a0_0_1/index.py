from fastapi import APIRouter

from app.api.v_a0_0_1.airsim.launch import router as airsim_launch_router

api_router = APIRouter()
api_router.include_router(airsim_launch_router, prefix="/airsim")
