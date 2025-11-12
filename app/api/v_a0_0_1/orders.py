"""This module defines the API routes for managing delivery orders."""

import json
import uuid

from fastapi import APIRouter, HTTPException, Request, Response, status

from app.services.airsim import execution
from app.services.delivery import schemas, service
from app.services.delivery.service import NoAvailableDronesError

router = APIRouter()


@router.post("/create", status_code=status.HTTP_201_CREATED)
def create_new_order(order_request: schemas.OrderCreateRequest) -> dict:
    """Create a new delivery order and enqueue it to an available drone.

    Notes:
    - Returns HTTP 409 when no drones are available (domain error is propagted.)
    - Returns HTTP 500 when an order ID could not be generated (unexpected state).
    - On success, returns the newly created order_id for subsequent tracking.
    """
    try:
        # 1) Persist the new order in the service layer
        created_order = service.process_new_order(order_request)

        # 2) Enqueue the order to an available Airsim drone
        execution.enqueue_order(created_order)

    except NoAvailableDronesError as e:
        # No idle drones at the moment: surface as 409 Conflict
        raise HTTPException(status_code=409, detail=str(e)) from e

    if not created_order.order_id:
        # Defensive check: creation should always yield an identifier
        raise HTTPException(status_code=500, detail="Order ID was not generated")

    # Minimal success payload to the client for tracking
    return {"message": "Order created successfully", "order_id": created_order.order_id}


# @router.get("/get_drone_data_by_order/{order_id}", status_code=status.HTTP_200_OK)
# def get_drone_data_by_order(order_id: int) -> dict:
#     """Return live drone data plus the latest captured image as multipart/mixed.

#     This endpoint fetches:
#     - data: a JSON-serializable telemetry dict (position, etc.)
#     - img: either raw PNG bytes, or a dict in the form {"image": (name, bytes, mime)}

#     The response body is constructed as a multipart/mixed entity containing:
#     - Part 1 (application/json; charset=utf-8): the telemetry JSON
#     - Part 2 (image/png): the PNG image bytes with a Content-Disposition filename

#     The multipart boundary is generated per response to avoid collisions in caches.
#     """
#     # Delegates to the AirSim execution layer; expected to return (data, img)
#     drone_data = execution.get_drone_progress(order_id)  # (data, img)
#     if not drone_data:
#         # No running drone found for this order (or not yet assigned)
#         raise HTTPException(status_code=404, detail="Drone data not found")

#     data, img = drone_data

#     # Default media metadata for the image part
#     mime = "image/png"
#     filename = "capture.png"

#     # Normalize the image payload into bytes + filename + mime
#     if isinstance(img, dict) and "image" in img:
#         # image payload format: ("capture", <PNG bytes>, "image/png")
#         name, img_bytes, mime = img["image"]
#         # Add extension if upstream returned a base name only
#         filename = f"{name}.png"
#     elif isinstance(img, bytes):
#         # Upstream returned bare PNG bytes
#         img_bytes = img
#     else:
#         # Unexpected payload shape: surface as a server error
#         raise HTTPException(status_code=500, detail="Invalid image payload")

#     # Optional: enable this block to validate PNG structure before responding.
#     # This helps fail fast when a corrupted or partial image is detected.
#     #
#     # ok, reason = _is_valid_png(img_bytes, expect_wh=(960, 720))
#     # if not ok:
#     #     # Return 500 to signal the image part cannot be trusted
#     #     raise HTTPException(status_code=500, detail=f"Corrupted PNG: {reason}")

#     # Generate a unique multipart boundary token for this response
#     boundary = f"mixed_{uuid.uuid4().hex}"

#     # Part 1: JSON (telemetry).
#     # According to MIME rules, headers are separated from body by a blank line,
#     # lines end with CRLF, and each part starts with "--<boundary>" on its own line.
#     part_json = (
#         f"--{boundary}\r\n"
#         "Content-Type: application/json; charset=utf-8\r\n\r\n"
#         f"{json.dumps(data, ensure_ascii=False)}\r\n"
#     ).encode()

#     # Part 2: Image (PNG).
#     # Content-Disposition includes a stable filename to aid downstream consumers.
#     # If you want to be explicit, you may add "Content-Transfer-Encoding: binary".
#     part_png_headers = (
#         f"--{boundary}\r\n"
#         f"Content-Type: {mime}\r\n"
#         f'Content-Disposition: inline; name="image"; filename="{filename}"\r\n\r\n'
#     ).encode()

#     # Closing boundary marks the end of the multipart entity.
#     closing = f"\r\n--{boundary}--\r\n".encode()

#     # Assemble the final response body in the order: JSON part, PNG headers, PNG bytes, closing
#     body = part_json + part_png_headers + img_bytes + closing

#     # The media_type must match the multipart type with the generated boundary parameter
#     return Response(
#         content=body,
#         media_type=f"multipart/mixed; boundary={boundary}",
#         headers={
#             # Prevent caching to ensure fresh telemetry/image per request
#             "Cache-Control": "no-store"
#         },
#     )


@router.get("/get_drone_data_by_order/{order_id}", status_code=status.HTTP_200_OK)
def get_drone_data_by_order(order_id: int, request: Request, part: str | None = None):
    # 1) 드론 진행 데이터 조회 (data: dict, img: bytes or dict 형태)
    drone_data = execution.get_drone_progress(order_id)
    if not drone_data:
        raise HTTPException(status_code=404, detail="Drone data not found")
    data, img = drone_data

    # 2) 이미지 바이트 정규화 (airsimutils에서 dict 형태로 오기도 함)
    mime = "image/png"
    filename = "capture.png"
    if isinstance(img, dict) and "image" in img:
        name, img_bytes, mime = img["image"]
        filename = f"{name}.png"
    elif isinstance(img, (bytes, bytearray)):
        img_bytes = bytes(img)
    else:
        raise HTTPException(status_code=500, detail="Invalid image payload")

    # 3) 쿼리 파라미터 최우선
    if part == "image":
        return Response(content=img_bytes, media_type=mime, headers={"Cache-Control": "no-store"})
    if part == "status":
        return Response(
            content=json.dumps(data, ensure_ascii=False),
            media_type="application/json; charset=utf-8",
            headers={"Cache-Control": "no-store"},
        )

    # 4) Accept 헤더 기반 분기
    accept = (request.headers.get("accept") or "").lower()
    # 프록시의 이미지 호출은 application/octet-stream을 포함하므로 이미지로 분기
    if "image/png" in accept or "application/octet-stream" in accept:
        return Response(content=img_bytes, media_type=mime, headers={"Cache-Control": "no-store"})
    if "application/json" in accept or "application/*+json" in accept:
        return Response(
            content=json.dumps(data, ensure_ascii=False),
            media_type="application/json; charset=utf-8",
            headers={"Cache-Control": "no-store"},
        )

    # 5) 기본: 하위 호환 multipart/mixed
    boundary = f"mixed_{uuid.uuid4().hex}"
    part_json = (
        f"--{boundary}\r\n"
        "Content-Type: application/json; charset=utf-8\r\n\r\n"
        f"{json.dumps(data, ensure_ascii=False)}\r\n"
    ).encode()
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
