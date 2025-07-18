from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, Enum as SqlEnum, create_engine
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime, timezone, timedelta
from enum import Enum

Base = declarative_base()
kst = timezone(timedelta(hours=9))  # Korea Standard Time (UTC+9)

class OrderStatus(str, Enum):
    """
    Order Status Enum

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
    """
    Order model 

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
    update_time = Column(DateTime, default=lambda: datetime.now(kst), onupdate=lambda: datetime.now(kst))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if 'create_time' not in kwargs:
            self.create_time = datetime.now(kst)
        if 'update_time' not in kwargs:
            self.update_time = datetime.now(kst)