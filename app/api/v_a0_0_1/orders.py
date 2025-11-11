"""This module defines the API routes for managing delivery orders."""

import json
import uuid

from fastapi import APIRouter, HTTPException, Response, status

from app.services.airsim import execution
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
    drone_data = execution.get_drone_progress(order_id)  # (data, img)

    if not drone_data:
        raise HTTPException(status_code=404, detail="Drone data not found")

    data, img = drone_data

    mime = "image/png"
    filename = "capture.png"
    if isinstance(img, dict) and "image" in img:
        name, img_bytes, mime = img[
            "image"
        ]  # name="capture", img_bytes=PNG bytes, mime="image/png"
        filename = f"{name}.png"
    elif isinstance(img, bytes):
        img_bytes = img
    else:
        raise HTTPException(status_code=500, detail="Invalid image payload")

    boundary = f"mixed_{uuid.uuid4().hex}"
    # JSON 파트
    part_json = (
        f"--{boundary}\r\n"
        "Content-Type: application/json; charset=utf-8\r\n\r\n"
        f"{json.dumps(data, ensure_ascii=False)}\r\n"
    ).encode()
    # PNG 파트
    part_png_headers = (
        f"--{boundary}\r\n"
        f"Content-Type: {mime}\r\n"
        f'Content-Disposition: inline; name="image"; filename="{filename}"\r\n\r\n'
    ).encode()
    closing = f"\r\n--{boundary}--\r\n".encode()

    body = part_json + part_png_headers + img_bytes + closing
    return Response(
        content=body,
        media_type=f"multipart/mixed; boundary={boundary}",
        headers={"Cache-Control": "no-store"},
    )
