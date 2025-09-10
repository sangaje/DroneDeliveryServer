"""This module handles the business logic for delivery orders."""

from app.models.order import Order
import app.services.controller.order_service as order_service
from app.services.delivery import schemas


def process_new_order(order_data: schemas.OrderCreateRequest) -> Order:
    """Process a new delivery order request."""
    db_order_data = {
        "receive_lat": order_data.pickup_location.latitude,
        "receive_lon": order_data.pickup_location.longitude,
        "receive_alt": order_data.pickup_location.altitude,
        "deliver_lat": order_data.delivery_location.latitude,
        "deliver_lon": order_data.delivery_location.longitude,
        "deliver_alt": order_data.delivery_location.altitude,
        # TODO: Implement drone selection logic based on item weight
    }

    return order_service.create_order(**db_order_data)
