"""Test cases for the order service controller."""

from app.models.drone import DroneStatus
from app.models.order import OrderStatus
import app.services.controller.drone_service as drone_service
import app.services.controller.order_service as order_service
from app.services.controller.order_service import OrderCreationError
import pytest
from sqlalchemy.orm import Session


@pytest.fixture(autouse=True)
def patch_session_local(monkeypatch: pytest.MonkeyPatch, session: Session) -> None:
    """Patch the session local for testing."""
    monkeypatch.setattr(order_service, "SessionLocal", lambda: session)
    monkeypatch.setattr(drone_service, "SessionLocal", lambda: session)


@pytest.fixture
def test_drone() -> drone_service.Drone:
    """Fixture to create a test drone."""
    drone_data = {
        "drone_id": 1,
        "status": DroneStatus.IDLE,
        "max_battery": 10000.0,
        "cur_battery": 10000.0,
        "max_payload": 5.0,
        "cur_payload": 0.0,
        "cur_lat": 37.0,
        "cur_lon": 127.0,
        "cur_alt": 10.0,
    }
    drone = drone_service.create_drone(drone_id=1, **drone_data)
    assert drone is not None

    return drone


def test_create_and_get_order(test_drone: drone_service.Drone) -> None:
    """Test creating and retrieving an order."""
    order_data = {
        "drone_id": test_drone.drone_id,
        "order_status": OrderStatus.PENDING,
        "receive_lat": 37.1,
        "receive_lon": 127.1,
        "receive_alt": 20.0,
        "deliver_lat": 37.2,
        "deliver_lon": 127.2,
        "deliver_alt": 30.0,
    }
    created_order = order_service.create_order(**order_data)
    assert created_order is not None
    assert created_order.order_id is not None
    assert created_order.drone_id == test_drone.drone_id
    assert created_order.order_status == OrderStatus.PENDING

    retrieved_order = order_service.get_order(created_order.order_id)
    assert retrieved_order is not None
    assert retrieved_order.order_id == created_order.order_id
    assert retrieved_order.drone_id == created_order.drone_id
    assert retrieved_order.order_status == created_order.order_status


def test_update_order(test_drone: drone_service.Drone) -> None:
    """Test updating an order."""
    order_data = {
        "drone_id": test_drone.drone_id,
        "order_status": OrderStatus.PENDING,
        "receive_lat": 37.1,
        "receive_lon": 127.1,
        "receive_alt": 20.0,
        "deliver_lat": 37.2,
        "deliver_lon": 127.2,
        "deliver_alt": 30.0,
    }
    created_order = order_service.create_order(**order_data)
    assert created_order is not None
    assert created_order.order_id is not None
    update_data = {"order_status": OrderStatus.DELIVERED}
    updated_order = order_service.update_order(
        created_order.order_id, order_update=None, **update_data
    )
    assert updated_order is not None
    assert updated_order.order_id is not None
    assert updated_order.order_status == OrderStatus.DELIVERED


def test_update_order_with_object(test_drone: drone_service.Drone) -> None:
    """Test updating an order with an order object."""
    order_data = {
        "drone_id": test_drone.drone_id,
        "order_status": OrderStatus.PENDING,
        "receive_lat": 37.1,
        "receive_lon": 127.1,
        "receive_alt": 20.0,
        "deliver_lat": 37.2,
        "deliver_lon": 127.2,
        "deliver_alt": 30.0,
    }
    created_order = order_service.create_order(**order_data)
    assert created_order is not None
    assert created_order.order_id is not None

    new_data = {
        "drone_id": test_drone.drone_id,
        "order_status": OrderStatus.ACCEPTED,
        "receive_lat": 37.1,
        "receive_lon": 127.1,
        "receive_alt": 20.0,
        "deliver_lat": 37.2,
        "deliver_lon": 127.2,
        "deliver_alt": 30.0,
    }
    new_order = order_service.create_order(**new_data)
    assert new_order is not None
    assert new_order.order_id is not None

    updated_order = order_service.update_order(
        order_id=created_order.order_id, order_update=new_order
    )
    assert updated_order is not None
    assert updated_order.order_id is not None
    assert updated_order.order_status == OrderStatus.ACCEPTED


def test_delete_order(test_drone: drone_service.Drone) -> None:
    """Test deleting an order."""
    order_data = {
        "drone_id": test_drone.drone_id,
        "order_status": OrderStatus.PENDING,
        "receive_lat": 37.1,
        "receive_lon": 127.1,
        "receive_alt": 20.0,
        "deliver_lat": 37.2,
        "deliver_lon": 127.2,
        "deliver_alt": 30.0,
    }
    created_order = order_service.create_order(**order_data)
    assert created_order.order_id is not None
    assert created_order is not None

    is_deleted = order_service.delete_order(created_order.order_id)
    assert is_deleted is True
    assert order_service.get_order(created_order.order_id) is None


def test_created_order_with_nonexist_drone() -> None:
    """Test creating an order with a non-existent drone."""
    order_data = {
        "drone_id": 999,
        "receive_lat": 37.1,
        "receive_lon": 127.1,
        "receive_alt": 20,
        "deliver_lat": 37.2,
        "deliver_lon": 127.2,
        "deliver_alt": 30,
    }

    with pytest.raises(OrderCreationError):
        order_service.create_order(**order_data)
