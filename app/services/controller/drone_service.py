"""TODO: Add a description of the module here."""

from app.models.drone import Drone
from app.services.controller.database import SessionLocal


def create_drone(**kwargs: dict) -> Drone | None:
    """Create a new drone record in the database.

    Args:
        **kwargs: Keyword arguments representing drone attributes.

    Returns:
        Drone: The created drone object if successful, None otherwise.
    """
    db = SessionLocal()
    drone = Drone(**kwargs)
    try:
        db.add(drone)
        db.commit()
        db.refresh(drone)
    except Exception as e:
        db.rollback()
        print(f"Error creating drone: {e}")
        return None
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
        return db.query(Drone).filter(Drone.id == drone_id).first()
    except Exception as e:
        print(f"Error retrieving drone: {e}")
        return None
    finally:
        db.close()


def get_all_drones() -> list[Drone]:
    """Retrieve all drone records from the database.

    Returns:
        List[Drone]: A list of all drone objects.
    """
    db = SessionLocal()
    try:
        return db.query(Drone).all()
    except Exception as e:
        print(f"Error retrieving all drones: {e}")
        return []
    finally:
        db.close()


def update_drone(drone_id: int, **kwargs: dict) -> Drone | None:
    """Update an existing drone record by its ID.

    Args:
        drone_id (int): The ID of the drone to update.
        **kwargs: Keyword arguments representing the attributes to update.

    Returns:
        Drone: The updated drone object if successful, None otherwise.
    """
    db = SessionLocal()
    try:
        drone = db.query(Drone).filter(Drone.id == drone_id).first()
        if not drone:
            return None

        for key, value in kwargs.items():
            setattr(drone, key, value)

        db.commit()
        db.refresh(drone)
        return drone
    finally:
        db.close()


def delete_drone(drone_id: int) -> Drone | None:
    """Delete a drone record by its ID.

    Args:
        drone_id (int): The ID of the drone to delete.

    Returns:
        Drone: The deleted drone object if successful, None otherwise.
    """
    db = SessionLocal()
    try:
        drone = db.query(Drone).filter(Drone.id == drone_id).first()
        if not drone:
            return None

        db.delete(drone)
        db.commit()
        return drone
    finally:
        db.close()
