"""This module handles the business logic for delivery orders."""

from app.models.drone import Drone, DroneStatus
from app.models.order import Order, OrderStatus
import app.services.controller.drone_service as drone_service
import app.services.controller.order_service as order_service
from app.services.delivery import schemas
from geopy.distance import geodesic


class NoAvailableDronesError(Exception):
    """Exception raised when no drones are available for a new order."""

    def __init__(self, message: str = "No available drones to process the order.") -> None:
        """Initialize the exception with a message."""
        self.message = message
        super().__init__(self.message)


def _find_closest_available_drone(latitude: float, longitude: float) -> Drone | None:
    """Find the closest available drone to the given coordinates."""
    available_drones = drone_service.get_all_drones()
    if not available_drones:
        return None

    idle_drones = [drone for drone in available_drones if drone.status == DroneStatus.IDLE]
    if not idle_drones:
        return None

    return min(
        idle_drones,
        key=lambda drone: geodesic((latitude, longitude), (drone.cur_lat, drone.cur_lon)).meters,
    )


def process_new_order(order_data: schemas.OrderCreateRequest) -> Order:
    """Process a new delivery order request."""
    # 1. Find the closest available drone to the store
    closest_drone = _find_closest_available_drone(
        order_data.store_latitude, order_data.store_longitude
    )
    if not closest_drone:
        raise NoAvailableDronesError

    # 2. Aggregate item_count from request items
    total_item_count = sum(item.quantity for item in order_data.items)

    # 3. Prepare order data for database creation
    db_order_data = {
        "order_id": order_data.order_id,
        "drone_id": closest_drone.drone_id,
        "order_status": OrderStatus.PENDING,
        "item_count": total_item_count,
        "receive_lat": order_data.store_latitude,
        "receive_lon": order_data.store_longitude,
        "deliver_lat": order_data.user_latitude,
        "deliver_lon": order_data.user_longitude,
        # Assuming a default altitude for now
        "receive_alt": 30.0,
        "deliver_alt": 30.0,
    }

    # 4. Create the order
    new_order = order_service.create_order(**db_order_data)

    # 5 . Update the drone's status to indicate it's on a mission
    # drone_service.update_drone(drone_id=closest_drone.drone_id, status=DroneStatus.DELIVERING)

    return new_order
