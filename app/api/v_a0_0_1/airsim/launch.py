from app.services.airsim.execution import init_session
from fastapi import APIRouter, Form, HTTPException, status

router = APIRouter()


@router.post("/launch", status_code=status.HTTP_200_OK)
def launch_airsim_session(config_name: str | None = Form(None)) -> dict:
    try:
        if not config_name:
            raise HTTPException(status_code=422, detail="config_name is required")
        airsim_config = {"LocalHostIp": "127.0.0.1", "ApiServerPort": 41451}
        init_session(airsim_config)
    except RuntimeError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AirSim launch failed: {e}") from e
    return {"message": "AirSim session launched and drones registered"}
