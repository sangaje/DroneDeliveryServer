"""This module defines the API routes for managing delivery orders."""

from fastapi import APIRouter, HTTPException, status

from app.services.delivery import schemas, service
from app.services.delivery.service import NoAvailableDronesError
from app.services.airsim import execution 

router = APIRouter()


@router.post("/create", status_code=status.HTTP_201_CREATED)
def create_new_order(order_request: schemas.OrderCreateRequest) -> dict:
    """Create a new delivery order.

    Notes:
    - Raises HTTP 409 when no drones are available (chained from domain error).
    - Raises HTTP 500 when an order ID could not be generated (unexpected state).
    """
    try:
        # 1. create the new order
        created_order = service.process_new_order(order_request)
        
        # 2. load list of available drones
        execution.enqueue_order(created_order)

    except NoAvailableDronesError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e

    if not created_order.order_id:
        raise HTTPException(status_code=500, detail="Order ID was not generated")

    return {"message": "Order created successfully", "order_id": created_order.order_id}

@router.get("/get_drone_data_by_order/{order_id}", status_code=status.HTTP_200_OK)
def get_drone_data_by_order(order_id: int) -> dict:
    """Get drone data associated with a specific order ID."""
    drone_data = execution.get_drone_data(order_id)
    if not drone_data:
        raise HTTPException(status_code=404, detail="Drone data not found")
    return {"drone_data": drone_data}