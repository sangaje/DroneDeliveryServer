"""This module defines the API routes for managing delivery orders."""

from fastapi import APIRouter, HTTPException, status

from app.services.delivery import schemas, service
from app.services.delivery.service import NoAvailableDronesError

router = APIRouter()


@router.post("/create", status_code=status.HTTP_201_CREATED)
def create_new_order(order_request: schemas.OrderCreateRequest) -> dict:
    """Create a new delivery order.

    Notes:
    - Raises HTTP 409 when no drones are available (chained from domain error).
    - Raises HTTP 500 when an order ID could not be generated (unexpected state).
    """
    try:
        created_order = service.process_new_order(order_request)
    except NoAvailableDronesError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e

    if not created_order.order_id:
        raise HTTPException(status_code=500, detail="Order ID was not generated")

    return {"message": "Order created successfully", "order_id": created_order.order_id}
