"""TODO: Add a description of the module here."""

from typing import Any

from app.models.order import Order
from app.services.controller.database import SessionLocal


# Custom exceptions for OrderService
class OrderServiceError(Exception):
    """Custom exception for OrderService errors."""

    pass


class OrderCreationError(OrderServiceError):
    """Exception raised when there is an error creating an order."""

    def __init__(self, msg: str = "Error creating order.") -> None:
        """Initialize the exception with a custom message.

        Args:
            msg (str): Custom error message.
        """
        self.msg = msg
        super().__init__(msg)


class OrderNotFoundError(OrderServiceError):
    """Exception raised when an order is not found."""

    def __init__(self, msg: str = "Order not found.") -> None:
        """Initialize the exception with a custom message.

        Args:
            msg (str): Custom error message.
        """
        self.msg = msg
        super().__init__(msg)


class OrderRetrievalError(OrderServiceError):
    """Exception raised when there is an error retrieving orders."""

    def __init__(self, msg: str = "Error retrieving orders.") -> None:
        """Initialize the exception with a custom message.

        Args:
            msg (str): Custom error message.
        """
        self.msg = msg
        super().__init__(msg)


class OrderUpdateError(OrderServiceError):
    """Exception raised when there is an error updating an order."""

    def __init__(self, msg: str = "Error updating order.") -> None:
        """Initialize the exception with a custom message.

        Args:
            msg (str): Custom error message.
        """
        self.msg = msg
        super().__init__(msg)


class OrderDeletionError(OrderServiceError):
    """Exception raised when there is an error deleting an order."""

    def __init__(self, msg: str = "Error deleting order.") -> None:
        """Initialize the exception with a custom message.

        Args:
            msg (str): Custom error message.
        """
        self.msg = msg
        super().__init__(msg)


def create_order(**kwargs: Any) -> Order:
    """Create a new order record in the database.

    This function accepts keyword arguments to set the attributes of the Order model.

    :param drone_id(Integer): The foreign key linking to the assigned drone.
    :param order_status(OrderStatus): The current status of the order.
    :param receive_lat(float): The latitude of the pickup location.
    :param receive_lon(float): The longitude of the pickup location.
    :param receive_alt(float): The altitude of the pickup location.
    :param deliver_lat(float): The latitude of the delivery destination.
    :param deliver_lon(float): The longitude of the delivery destination.
    :param deliver_alt(float): The altitude of the delivery destination.
    :return: The created order object.
    :raises OrderCreationError: If the order creation fails.
    """
    db = SessionLocal()
    order = Order(**kwargs)
    try:
        db.add(order)
        db.commit()
        db.refresh(order)
    except Exception as e:
        db.rollback()
        raise OrderCreationError from e
    finally:
        db.close()
    return order


def get_order(order_id: int) -> Order | None:
    """Retrieve an order record by its ID.

    Args:
        order_id (int): The ID of the order to retrieve.

    Returns:
        Order | None: The order object if found, otherwise None.
    """
    db = SessionLocal()
    try:
        return db.query(Order).filter(Order.order_id == order_id).first()
    except Exception as e:
        raise OrderNotFoundError from e
    finally:
        db.close()


def get_all_orders() -> list[Order]:
    """Retrieve all order records from the database.

    Returns:
        list[Order]: A list of all order objects. An empty list is returned if no orders are found.
    """
    db = SessionLocal()
    try:
        return db.query(Order).all()
    except Exception as e:
        raise OrderRetrievalError from e
    finally:
        db.close()


def update_order(
    order_id: int, order_update: Order | None = None, **kwargs: Any | None
) -> Order | None:
    """Update an existing order record by its ID.

    This function can update an order using either an Order object or keyword arguments.

    :param order_id(int): The ID of the order to update. :param order_update(Order | None): An Order
        object with updated values.
    :param kwargs: Keyword arguments with attributes to update.
    :return: The updated order object if successful, None otherwise.
    :raises OrderUpdateError: If the order update fails.
    """
    db = SessionLocal()
    try:
        db_order = db.query(Order).filter(Order.order_id == order_id).first()

        if not db_order:
            return None

        update_data = {}
        if order_update:
            update_data = {
                c.name: getattr(order_update, c.name)
                for c in order_update.__table__.columns
                if c.name != "order_id" and getattr(order_update, c.name) is not None
            }

        update_data.update(kwargs)

        for key, value in update_data.items():
            setattr(db_order, key, value)

        db.commit()
        db.refresh(db_order)
    except Exception as e:
        db.rollback()
        raise OrderUpdateError from e
    finally:
        db.close()

    return db_order


def delete_order(order_id: int) -> bool:
    """Delete an order record by its ID.

    Args:
        order_id (int): The ID of the order to delete.

    Returns:
        bool: True if deletion was successful, False otherwise.
    """
    db = SessionLocal()
    try:
        order = db.query(Order).filter(Order.order_id == order_id).first()
        if not order:
            return False

        db.delete(order)
        db.commit()
    except Exception as e:
        db.rollback()
        raise OrderDeletionError from e
    finally:
        db.close()

    return True
