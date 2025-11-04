"""This module defines the Pydantic schemas for handling delivery order requests.

These schemas are used for data validation and serialization when processing incoming API requests
related to delivery orders.
"""

from pydantic import BaseModel, Field


class FoodItem(BaseModel):
    """Represents a single food item within an order."""

    foodname: str = Field(..., alias="foodName", min_length=1, description="The name of the food.")
    quantity: int = Field(..., alias="quantity", gt=0, description="The quantity of the food.")


class OrderCreateRequest(BaseModel):
    """Schema for a new order creation request, matching the provided JSON structure."""

    items: list[FoodItem] = Field(
        ..., min_length=1, description="A list of food items in the order."
    )

    store_latitude: float = Field(..., alias="storeLatitude", ge=-90.0, le=90.0)
    store_longitude: float = Field(..., alias="storeLongitude", ge=-180.0, le=180.0)
    user_latitude: float = Field(..., alias="userLatitude", ge=-90.0, le=90.0)
    user_longitude: float = Field(..., alias="userLongitude", ge=-180.0, le=180.0)

    class Config:
        """Pydantic model configuration class."""

        populate_by_name = True

        json_schema_extra = {
            "example": {
                "items": [
                    {"foodName": "불싸이순살", "quantity": 1},
                    {"foodName": "싸이순살", "quantity": 1},
                ],
                "storeLatitude": 37.691887,
                "userLatitude": 37.566370,
                "storeLongitude": 127.213920,
                "userLongitude": 126.977918,
            }
        }
