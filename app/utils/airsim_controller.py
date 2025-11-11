"""This module provides an interface to control a drone in AirSim using Python."""

import cosysairsim as airsim
import pymap3d as pm


def lla_to_ned(
    origin_lat: float,
    origin_lon: float,
    origin_alt: float,
    target_lat: float,
    target_lon: float,
    target_alt: float,
) -> tuple:
    """Convert latitude, longitude, and altitude to North-East-Down (NED) coordinates.

    Args:
        origin_lat (float): Latitude of the origin point.
        origin_lon (float): Longitude of the origin point.
        origin_alt (float): Altitude of the origin point.
        target_lat (float): Latitude of the target point.
        target_lon (float): Longitude of the target point.
        target_alt (float): Altitude of the target point.

    Returns:
        tuple: A tuple containing the NED coordinates (north, east, down).
    """
    return pm.geodetic2ned(target_lat, target_lon, target_alt, origin_lat, origin_lon, origin_alt)


class AirSimController:
    """Controller for interacting with AirSim drones."""

    def __init__(self) -> None:
        """Initialize the AirSim client."""
        self.client = airsim.MultirotorClient()
        self.client.confirmConnection()
        self.client.enableApiControl(True)

    def get_all_drones_info(self) -> dict[str, airsim.MultirotorState]:
        """Get the state of all drones in the simulation.

        Returns:
            A dictionary where keys are drone names and values are their states.
        """
        vehicle_names = self.client.listVehicles()
        drones_info = {}

        for name in vehicle_names:
            self.client.enableApiControl(True, vehicle_name=name)
            drones_info[name] = self.client.getMultirotorState(vehicle_name=name)

        return drones_info

    def get_home_geo_point(self) -> airsim.GeoPoint:
        """Get the home geo point of the simulation origin."""
        return self.client.getHomeGeoPoint()

    async def takeoff(self) -> None:
        """Command the drone to take off."""
        await self.client.takeoffAsync().join()

    async def move_to_position(self, x: float, y: float, z: float, velocity: float) -> None:
        """Move the drone to a specified position.

        Args:
            x (float): The distance to move in the x-direction (NED).
            y (float): The distance to move in the y-direction (NED).
            z (float): The distance to move in the z-direction (NED).
            velocity (float): The speed at which to move.
        """
        await self.client.moveToPositionAsync(x, y, z, velocity).join()

    async def land(self) -> None:
        """Command the drone to land."""
        await self.client.landAsync().join()
