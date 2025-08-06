"""TODO: Add a description of the module here."""

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


def create_order(**kwargs: dict) -> Order | None:
    """Create a new order record in the database.

    Args:
        **kwargs: Keyword arguments representing order attributes.

    Returns:
        Order: The created order object if successful, None otherwise.
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
        Order: The order object if found.
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
        List[Order]: A list of all order objects.
    """
    db = SessionLocal()
    try:
        return db.query(Order).all()
    except Exception as e:
        raise OrderRetrievalError from e
    finally:
        db.close()


def update_order(order_id: int, **kwargs: dict) -> Order | None:
    """Update an existing order record by its ID.

    Args:
        order_id (int): The ID of the order to update.
        **kwargs: Keyword arguments representing the attributes to update.

    Returns:
        Order: The updated order object if successful, None otherwise.
    """
    db = SessionLocal()
    try:
        order = db.query(Order).filter(Order.order_id == order_id).first()
        if not order:
            return None

        for key, value in kwargs.items():
            setattr(order, key, value)

        db.commit()
        db.refresh(order)
    except Exception as e:
        db.rollback()
        raise OrderUpdateError from e
    finally:
        db.close()

    return order


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
