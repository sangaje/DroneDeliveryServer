from pydantic import BaseModel

class DroneCommand(BaseModel):
    command: str # Command to be sent to the drone

class DroneStatus(BaseModel):
    id: int                  # Unique identifier for the drone
    status: str              # Current status of the drone
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
            status="active",
            latitude=37.5665,
            longitude=126.9780
        )
        self.assertEqual(status.id, 1)
        self.assertEqual(status.status, "active")
        self.assertEqual(status.latitude, 37.5665)
        self.assertEqual(status.longitude, 126.9780)

if __name__ == "__main__":
    unittest.main()