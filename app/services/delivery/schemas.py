"""This module defines the Pydantic schemas for handling delivery order requests.

These schemas are used for data validation and serialization when processing
incoming API requests related to delivery orders.
"""

from pydantic import BaseModel, Field


class Location(BaseModel):
    """Represents a geographical location with latitude, longitude, and altitude."""

    latitude: float = Field(
        ..., ge=-90.0, le=90.0, description="The latitude of the location, in degrees."
    )
    longitude: float = Field(
        ..., ge=-180.0, le=180.0, description="The longitude of the location, in degrees."
    )
    altitude: float = Field(..., description="The altitude of the location, in meters.")


class Item(BaseModel):
    """Represents an item to be delivered."""

    name: str = Field(
        ..., min_length=1, max_length=100, description="The name of the item being delivered."
    )
    weight_kg: float = Field(
        ..., gt=0, description="The weight of the item in kilograms. Must be greater than 0."
    )


class OrderCreateRequest(BaseModel):
    """Schema for a new order creation request coming from the web server."""

    external_order_id: str = Field(
        ...,
        min_length=1,
        description="The unique order ID from the external web (Delivery Server).",
    )
    pickup_location: Location
    delivery_location: Location
    item: Item

    class Config:
        """Pydantic model configuration class."""

        json_schema_extra = {
            "example": {
                "external_order_id": "WEB-ORDER-12345",
                "pickup_location": {"latitude": 37.4938, "longitude": 127.4896, "altitude": 50.0},
                "delivery_location": {"latitude": 37.4904, "longitude": 127.4941, "altitude": 60.0},
                "item": {"name": "Fried Chicken", "weight_kg": 1.5},
            }
        }
