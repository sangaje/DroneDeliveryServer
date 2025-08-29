"""Test cases for the models."""

from app.models.drone import Drone, DroneStatus
from app.models.order import Order, OrderStatus
from sqlalchemy.orm import Session


def test_create_drone(session: Session) -> None:
    """Test creating a drone."""
    drone_data = {
        "status": DroneStatus.IDLE,
        "max_battery": 10000.0,
        "cur_battery": 9500.0,
        "max_payload": 10.0,
        "cur_payload": 0.0,
        "cur_lat": 37.5,
        "cur_lon": 127.5,
        "cur_alt": 10.0,
    }
    drone = Drone(**drone_data)

    session.add(drone)
    session.commit()
    session.refresh(drone)

    retrieved_drone = session.query(Drone).filter(Drone.drone_id == drone.drone_id).first()

    assert retrieved_drone is not None
    assert retrieved_drone.status == DroneStatus.IDLE
    assert retrieved_drone.max_battery == 10000.0


def test_create_order_with_drone(session: Session) -> None:
    """Test creating an order associated with a drone."""
    drone = Drone(
        status=DroneStatus.IDLE,
        max_battery=10000,
        cur_battery=10000,
        max_payload=5,
        cur_payload=0,
        cur_lat=37.0,
        cur_lon=127.0,
        cur_alt=10,
    )
    session.add(drone)
    session.commit()
    session.refresh(drone)

    order_data = {
        "drone_id": drone.drone_id,
        "order_status": OrderStatus.PENDING,
        "receive_lat": 37.1,
        "receive_lon": 127.1,
        "receive_alt": 20,
        "deliver_lat": 37.2,
        "deliver_lon": 127.2,
        "deliver_alt": 30,
    }
    order = Order(**order_data)

    session.add(order)
    session.commit()
    session.refresh(order)

    retrieved_order = session.query(Order).filter(Order.order_id == order.order_id).first()

    assert retrieved_order is not None
    assert retrieved_order.drone_id == drone.drone_id
    assert retrieved_order.order_status == OrderStatus.PENDING
