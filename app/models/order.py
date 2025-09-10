"""TODO: Add docstring for the module."""

from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any

from sqlalchemy import Column, DateTime, Enum as SQLEnum, Float, ForeignKey, Integer

from app.models.base import Base

kst = timezone(timedelta(hours=9))  # Korea Standard Time (UTC+9)


class OrderStatus(str, Enum):
    """Order Status Enum.

    Attributes:
    - PENDING: The order has been created but not yet assigned to a drone.
    - ACCEPTED: The order has been assigned to a drone.
    - RECEIVED: The drone has picked up the package.
    - DELIVERED: The drone has successfully delivered the package.
    - FAILED: The delivery has failed.
    - CANCELED: The order has been canceled.
    """

    PENDING = "pending"
    ACCEPTED = "accepted"
    RECEIVED = "received"
    DELIVERED = "delivered"
    FAILED = "failed"
    CANCELED = "canceled"


class Order(Base):
    """Order model.

    Attributes:
    - order_id: The primary key for the order.
    - drone_id: The foreign key linking to the assigned drone.
    - order_status: The current status of the order, using the OrderStatus enum.
    - receive_lat: The latitude of the pickup location.
    - receive_lon: The longitude of the pickup location.
    - receive_alt: The altitude of the pickup location.
    - deliver_lat: The latitude of the delivery destination.
    - deliver_lon: The longitude of the delivery destination.
    - deliver_alt: The altitude of the delivery destination.
    - assigned_at: The timestamp when the order was created.
    - completed_at: The timestamp when the order was completed (delivered, failed, or canceled).
    """

    __tablename__ = "orders"
    order_id = Column(Integer, primary_key=True, autoincrement=True)
    drone_id = Column(Integer, ForeignKey("drones.drone_id"))
    order_status = Column(SQLEnum(OrderStatus), nullable=False, default=OrderStatus.PENDING)

    receive_lat = Column(Float, nullable=False)
    receive_lon = Column(Float, nullable=False)
    receive_alt = Column(Float, nullable=False)

    deliver_lat = Column(Float, nullable=False)
    deliver_lon = Column(Float, nullable=False)
    deliver_alt = Column(Float, nullable=False)

    assigned_at = Column(DateTime, default=datetime.now(kst))
    completed_at = Column(DateTime, nullable=True)

    def __init__(self, **kwargs: Any) -> None:
        """Initializes an Order instance.

        This constructor accepts keyword arguments to set the attributes of the Order model.

        :param drone_id(Integer): The foreign key linking to the assigned drone.
        :param order_status(SQLEnum(OrderStatus)): The current status of the order.
        :param receive_lat(Float): The latitude of the pickup location.
        :param receive_lon(Float): The longitude of the pickup location.
        :param receive_alt(Float): The altitude of the pickup location.
        :param deliver_lat(Float): The latitude of the delivery destination.
        :param deliver_lon(Float): The longitude of the delivery destination.
        :param deliver_alt(Float): The altitude of the delivery destination.
        :param assigned_at(DateTime): The timestamp when the order was created.
        :param completed_at(DateTime): The timestamp when the order was completed.
        """
        super().__init__(**kwargs)
