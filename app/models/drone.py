"""TODO: Add a description of the module here."""

from enum import Enum

from pydantic import BaseModel


class DroneStatusEnum(str, Enum):
    """Drone Status Enum.

    Attributes:
        IDLE: Drone is idle
        ACTIVE: Drone is active and operating
        CHARGING: Drone is charging
        MAINTENANCE: Drone is under maintenance
        ERROR: Drone has encountered an error
    """

    IDLE = "idle"
    ACTIVE = "active"
    CHARGING = "charging"
    MAINTENANCE = "maintenance"
    ERROR = "error"


class DroneCommand(BaseModel):
    """Drone Command Model.

    Attributes:
        drone_id: Unique identifier for the drone
        command: Command to be executed by the drone (e.g., start, stop, return)
    """

    drone_id: int
    command: str


class DroneStatus(BaseModel):
    """Drone Status Model.

    Attributes:
        drone_id: Unique identifier for the drone
        status: Current status of the drone (idle, active, charging, maintenance, error)
        latitude: Current latitude of the drone
        longitude: Current longitude of the drone
    """

    drone_id: int
    status: DroneStatusEnum
    latitude: float | None = None
    longitude: float | None = None
