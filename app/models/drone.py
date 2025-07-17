from pydantic import BaseModel

class DroneCommand(BaseModel):
    drone_id:   int     # unique identifier for the drone
    command:    str     # takeoff, land, move_to, etc.
    target_lat: float   # latitude
    target_lon: float   # longitude
    target_alt: float   # altitude

class DroneStatus(BaseModel):
    drone_id:   int     # unique identifier for the drone
    lat:        float   # latitude
    lon:        float   # longitude
    alt:        float   # altitude
    velocity:   float   # velocity
