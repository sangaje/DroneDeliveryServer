"""Test cases for the drone service controller."""

from app.models.drone import DroneStatus
import app.services.controller.drone_service as drone_service
import pytest
from sqlalchemy.orm import Session


@pytest.fixture(autouse=True)
def patch_session_local(monkeypatch: pytest.MonkeyPatch, session: Session) -> None:
    """Patch the session local for testing."""
    monkeypatch.setattr(drone_service, "SessionLocal", lambda: session)


def test_create_and_get_drone() -> None:
    """Test creating and retrieving a drone."""
    drone_data = {
        "drone_id": 1,
        "status": DroneStatus.IDLE,
        "max_battery": 10000.0,
        "cur_battery": 10000.0,
        "max_payload": 5.0,
        "cur_payload": 0.0,
        "cur_lat": 37.0,
        "cur_lon": 127.0,
        "cur_alt": 50.0,
    }
    created_drone = drone_service.create_drone(**drone_data)
    assert created_drone is not None
    assert created_drone.status == DroneStatus.IDLE
    assert created_drone.drone_id == 1

    retrieved_drone = drone_service.get_drone(drone_id=1)
    assert retrieved_drone is not None
    assert retrieved_drone.drone_id == created_drone.drone_id
    assert retrieved_drone.max_payload == created_drone.max_payload


def test_get_all_drones() -> None:
    """Test retrieving all drones."""
    first_drone_data = {
        "drone_id": 1,
        "status": DroneStatus.IDLE,
        "max_battery": 10000.0,
        "cur_battery": 10000.0,
        "max_payload": 5.0,
        "cur_payload": 0.0,
        "cur_lat": 37.0,
        "cur_lon": 127.0,
        "cur_alt": 50.0,
    }

    second_drone_data = {
        "drone_id": 2,
        "status": DroneStatus.IDLE,
        "max_battery": 10000.0,
        "cur_battery": 10000.0,
        "max_payload": 5.0,
        "cur_payload": 0.0,
        "cur_lat": 37.0,
        "cur_lon": 127.0,
        "cur_alt": 50.0,
    }

    drone_service.create_drone(**first_drone_data)
    drone_service.create_drone(**second_drone_data)

    all_drones = drone_service.get_all_drones()
    assert all_drones is not None
    assert len(all_drones) == 2


def test_update_drone() -> None:
    """Test updating a drone."""
    drone_data = {
        "drone_id": 1,
        "status": DroneStatus.IDLE,
        "max_battery": 10000.0,
        "cur_battery": 10000.0,
        "max_payload": 5.0,
        "cur_payload": 0.0,
        "cur_lat": 37.0,
        "cur_lon": 127.0,
        "cur_alt": 50.0,
    }
    drone_service.create_drone(**drone_data)

    updated_data = {"status": DroneStatus.DELIVERING, "cur_battery": 8000.0}

    updated_drone = drone_service.update_drone(drone_id=1, **updated_data)
    assert updated_drone is not None
    assert updated_drone.status == DroneStatus.DELIVERING
    assert updated_drone.cur_battery == 8000.0


def test_delete_drone() -> None:
    """Test deleting a drone."""
    drone_data = {
        "drone_id": 1,
        "status": DroneStatus.IDLE,
        "max_battery": 10000.0,
        "cur_battery": 10000.0,
        "max_payload": 5.0,
        "cur_payload": 0.0,
        "cur_lat": 37.0,
        "cur_lon": 127.0,
        "cur_alt": 50.0,
    }
    drone_service.create_drone(**drone_data)

    delete_result = drone_service.delete_drone(drone_id=1)
    assert delete_result is True

    retrieved_drone = drone_service.get_drone(drone_id=1)
    assert retrieved_drone is None


def test_get_nonexistent_drone() -> None:
    """Test retrieving a non-existent drone."""
    retrieved_drone = drone_service.get_drone(drone_id=999)
    assert retrieved_drone is None
