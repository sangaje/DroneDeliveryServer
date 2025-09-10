"""TODO: Add a description of the module here."""

from typing import Any

from app.models.drone import Drone
from app.services.controller.database import SessionLocal


# Custom exceptions for DroneService
class DroneServiceError(Exception):
    """Custom exception for DroneService errors."""

    pass


class DroneCreationError(DroneServiceError):
    """Exception raised when there is an error creating a drone."""

    def __init__(self, msg: str = "Error creating drone.") -> None:
        """Initialize the exception with a custom message.

        Args:
            msg (str): Custom error message.
        """
        self.msg = msg
        super().__init__(msg)


class DroneNotFoundError(DroneServiceError):
    """Exception raised when a drone is not found."""

    def __init__(self, msg: str = "Drone not found.") -> None:
        """Initialize the exception with a custom message.

        Args:
            msg (str): Custom error message.
        """
        self.msg = msg
        super().__init__(msg)


class DroneRetrievalError(DroneServiceError):
    """Exception raised when there is an error retrieving drones."""

    def __init__(self, msg: str = "Error retrieving drones.") -> None:
        """Initialize the exception with a custom message.

        Args:
            msg (str): Custom error message.
        """
        self.msg = msg
        super().__init__(msg)


class DroneUpdateError(DroneServiceError):
    """Exception raised when there is an error updating a drone."""

    def __init__(self, msg: str = "Error updating drone.") -> None:
        """Initialize the exception with a custom message.

        Args:
            msg (str): Custom error message.
        """
        self.msg = msg
        super().__init__(msg)


class DroneDeletionError(DroneServiceError):
    """Exception raised when there is an error deleting a drone."""

    def __init__(self, msg: str = "Error deleting drone.") -> None:
        """Initialize the exception with a custom message.

        Args:
            msg (str): Custom error message.
        """
        self.msg = msg
        super().__init__(msg)


def create_drone(**kwargs: Any) -> Drone:
    """Create a new drone record in the database.

    This function accepts keyword arguments to set the attributes of the Drone model.

    :param status(DroneStatus): The current status of the drone.
    :param max_battery(float): The maximum battery capacity in mAh.
    :param cur_battery(float): The current battery level in mAh.
    :param max_payload(float): The maximum payload weight the drone can carry in kg.
    :param cur_payload(float): The current payload weight the drone is carrying in kg.
    :param cur_lat(float): The current latitude of the drone.
    :param cur_lon(float): The current longitude of the drone.
    :param cur_alt(float): The current altitude of the drone in meters.
    :return: The created drone object.
    :raises DroneCreationError: If the drone creation fails.
    """
    db = SessionLocal()
    drone = Drone(**kwargs)
    try:
        db.add(drone)
        db.commit()
        db.refresh(drone)
    except Exception as e:
        db.rollback()
        raise DroneCreationError from e
    finally:
        db.close()
    return drone


def get_drone(drone_id: int) -> Drone | None:
    """Retrieve a drone record by its ID.

    Args:
        drone_id (int): The ID of the drone to retrieve.

    Returns:
        Drone: The drone object if found.
    """
    db = SessionLocal()
    try:
        return db.query(Drone).filter(Drone.drone_id == drone_id).first()
    except Exception as e:
        raise DroneNotFoundError from e
    finally:
        db.close()


def get_all_drones() -> list[Drone] | None:
    """Retrieve all drone records from the database.

    Returns:
        List[Drone]: A list of all drone objects.
    """
    db = SessionLocal()
    try:
        return db.query(Drone).all()
    except Exception as e:
        raise DroneRetrievalError from e
    finally:
        db.close()


def update_drone(drone_id: int, **kwargs: Any) -> Drone | None:
    """Update an existing drone record by its ID.

    This function accepts keyword arguments to update the attributes of the Drone model.

    :param drone_id(int): The ID of the drone to update.
    :param status(DroneStatus): The new status of the drone.
    :param cur_battery(float): The new battery level.
    :return: The updated drone object if successful, None otherwise.
    :raises DroneUpdateError: If the drone update fails.
    """
    db = SessionLocal()
    try:
        drone = db.query(Drone).filter(Drone.drone_id == drone_id).first()

        if not drone:
            return None

        for key, value in kwargs.items():
            setattr(drone, key, value)

        db.commit()
        db.refresh(drone)
    except Exception as e:
        db.rollback()
        raise DroneUpdateError from e
    finally:
        db.close()

    return drone


def delete_drone(drone_id: int) -> bool:
    """Delete a drone record by its ID.

    Args:
        drone_id (int): The ID of the drone to delete.

    Returns:
        bool: True if deletion was successful, False otherwise.
    """
    db = SessionLocal()
    try:
        drone = db.query(Drone).filter(Drone.drone_id == drone_id).first()

        if not drone:
            return False

        db.delete(drone)
        db.commit()
    except Exception as e:
        db.rollback()
        raise DroneDeletionError from e
    finally:
        db.close()

    return True
