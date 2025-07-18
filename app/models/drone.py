from pydantic import BaseModel
from enum import Enum

class DroneStatusEnum(str, Enum):
    """
    Drone Status Enum

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
    command: str # Command to be sent to the drone

class DroneStatus(BaseModel):
    id: int                  # Unique identifier for the drone
    status: DroneStatusEnum  # Current status of the drone
    latitude: float = None   # Current latitude of the drone
    longitude: float = None  # Current longitude of the drone



# Test area
import unittest

class TestDroneModels(unittest.TestCase):
    def test_drone_command(self):
        cmd = DroneCommand(command="takeoff")
        self.assertEqual(cmd.command, "takeoff")

    def test_drone_status(self):
        status = DroneStatus(
            id=1,
            status=DroneStatusEnum.ACTIVE,
            latitude=37.5665,
            longitude=126.9780
        )
        self.assertEqual(status.id, 1)
        self.assertEqual(status.status, DroneStatusEnum.ACTIVE)
        self.assertEqual(status.latitude, 37.5665)
        self.assertEqual(status.longitude, 126.9780)

if __name__ == "__main__":
    unittest.main()