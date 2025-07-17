from pydantic import BaseModel

class DroneCommand(BaseModel):
    drone_id: int
    command: str  # takeoff, land, move_to, etc.
    target_lat: float
    target_lon: float
    target_alt: float

class DroneStatus(BaseModel):
    drone_id: int
    lat: float
    lon: float
    alt: float
    velocity: float
