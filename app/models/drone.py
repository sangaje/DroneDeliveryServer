"""TODO: Add a description of the module here."""

from datetime import timedelta, timezone
from typing import Any

from sqlalchemy import Column, Enum, Float, Integer
from sqlalchemy.orm import declarative_base

Base = declarative_base()
kst = timezone(timedelta(hours=9))  # Korea Standard Time (UTC+9)


class DroneStatus(str, Enum):
    """Drone Status Enum.

    Attributes:
    - IDLE: Waiting for an order at the base.
    - CHARGING: Currently charging its battery.
    - MAINTAINING: Undergoing repairs or routine checks.
    - DELIVERING: In the process of delivering an order.
    - RETURNING: Returning to base after a delivery.
    """

    IDLE = "idle"
    CHARGING = "charging"
    MAINTAINING = "maintaining"
    DELIVERING = "delivering"
    RETURNING = "returning"


class Drone(Base):
    """Drone model.

    Attributes:
    - drone_id: The primary key for the drone.
    - drone_status: The current status of the drone, using the DroneStatus enum.
    - max_battery: The maximum battery capacity in mAh.
    - cur_battery: The current battery level in mAh.
    - max_payload: The maximum payload weight the drone can carry in kg.
    - cur_payload: The current payload weight the drone is carrying in kg.
    - cur_lat: The current latitude of the drone.
    - cur_lon: The current longitude of the drone.
    - cur_alt: The current altitude of the drone in meters.
    """

    __tablename__ = "drones"
    drone_id = Column(Integer, primary_key=True, autoincrement=True)
    drone_status = Column(DroneStatus, nullable=False, default=DroneStatus.IDLE)

    max_battery = Column(Float, nullable=False)
    cur_battery = Column(Float, nullable=False)

    max_payload = Column(Float, nullable=False)
    cur_payload = Column(Float, nullable=False)

    cur_lat = Column(Float, nullable=False)
    cur_lon = Column(Float, nullable=False)
    cur_alt = Column(Float, nullable=False)

    def __init__(self, **kwargs: Any) -> None:
        """Initializes a Drone instance.

        This constructor accepts keyword arguments to set the attributes of the Drone
        model.

        :param kwargs: Keyword arguments to initialize the drone.
        :return: None
        """
        super().__init__(**kwargs)
