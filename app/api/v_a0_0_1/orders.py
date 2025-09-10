"""This module defines the API routes for managing delivery orders."""

from fastapi import APIRouter, status

from app.services.delivery import schemas, service

router = APIRouter()


@router.post("/orders", status_code=status.HTTP_201_CREATED)
def create_new_order(order_request: schemas.OrderCreateRequest) -> dict | None:
    """Create a new delivery order."""
    # request.json()
    try:
        created_order = service.process_new_order(order_request)
    except Exception:
        pass

    return {"message": "Order created successfully", "order_id": created_order.order_id}
