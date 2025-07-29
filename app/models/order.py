"""TODO: Add a description of the module here."""

from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any

from sqlalchemy import Column, DateTime, Enum as SqlEnum, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()
kst = timezone(timedelta(hours=9))  # Korea Standard Time (UTC+9)


class OrderStatus(str, Enum):
    """Order Status Enum.

    Attributes:
        PENDING: Order is pending
        IN_PROGRESS: Order is being processed
        COMPLETED: Order has been completed
        CANCELLED: Order has been cancelled
        FAILED: Order processing has failed
    """

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class Order(Base):
    """Order model.

    Attributes:
        id: Unique identifier for the order
        member_id: Foreign key referencing the member who placed the order
        order_status: Status of the order (pending, in_progress, completed, cancelled, failed)
        drone_id: Foreign key referencing the drone assigned to the order
        products: JSON string containing product details
        create_time: Timestamp when the order was created
        update_time: Timestamp when the order was last updated
    """

    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    order_status = Column(SqlEnum(OrderStatus), nullable=False, default=OrderStatus.PENDING)
    drone_id = Column(Integer, ForeignKey("drones.id"))
    products = Column(String)
    create_time = Column(DateTime, default=lambda: datetime.now(kst))
    update_time = Column(
        DateTime, default=lambda: datetime.now(kst), onupdate=lambda: datetime.now(kst)
    )

    def __init__(self, **kwargs: Any) -> None:
        """TODO: Add a description of the constructor.

        :param kwargs: Keyword arguments to initialize the order.
        :return: None
        """
        super().__init__(**kwargs)
        if "create_time" not in kwargs:
            self.create_time = datetime.now(kst)
        if "update_time" not in kwargs:
            self.update_time = datetime.now(kst)
