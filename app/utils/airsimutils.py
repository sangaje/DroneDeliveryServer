"""TODO: Add module docstring."""

from __future__ import annotations

from logging import info

from cosysairsim import MultirotorClient, MultirotorState

_client: MultirotorClient | None = None


def disconnect_client() -> None:
    """Disconnect from the AirSim client."""
    global _client
    if _client:
        info("Disconnecting cosysairsim client...")
        _client.reset()
        _client = None
        info("cosysairsim client disconnected.")
    else:
        info("cosysairsim client is not connected.")


def connect_client(ip: str, port: int) -> None:
    """Connect to the AirSim client.

    :param ip: IP address of the AirSim simulator.
    :param port: Port number of the AirSim simulator.
    """
    global _client

    # Set up AirSim client
    if _client is None:
        info(f"Setting up cosysairsim client {ip}:{port}...")
        _client = MultirotorClient(ip=ip, port=port)
    else:
        info("cosysairsim client already connected.")

    if not _client.ping():
        raise ConnectionError(f"{ip}:{port}")

    info("cosysairsim client connected.")


def create_drones_list() -> list[Drone]:
    """List all drones in the AirSim simulation."""
    global _client
    if not _client:
        raise ConnectionError(_client)
    retval: list[Drone] = []
    vehicle_names = _client.listVehicles()
    if not vehicle_names:
        info("No vehicles found in the AirSim simulation.")
        return retval
    for drone in vehicle_names:
        try:
            state = _client.getMultirotorState(vehicle_name=drone)
            if isinstance(state, MultirotorState):
                retval.append(Drone(vehicle_name=drone))
        except Exception:
            pass
    return retval


class Drone:
    """Class representing a drone in the AirSim simulation."""

    _vehicle_name: str
    _client: MultirotorClient
    _state: MultirotorState

    def __init__(self, vehicle_name: str) -> None:
        """Initialize the Drone object.

        :param vehicle_name: The name of the drone in the AirSim simulation.
        """
        global _client
        self._vehicle_name = vehicle_name
        if not _client:
            raise ConnectionError(_client)
        self._client = _client
        self.update_state()

    @property
    def vehicle_name(self) -> str:
        """Get the vehicle name of the drone."""
        return self._vehicle_name

    @property
    def state(self) -> MultirotorState:
        """Get the current state of the drone."""
        return self._state

    @property
    def id(self) -> int:
        """Get a unique identifier for the drone instance."""
        return id(self)

    def update_state(self) -> MultirotorState:
        """Update and return the current state of the drone.

        :return: The current state of the drone.
        """
        self._state = self._client.getMultirotorState(vehicle_name=self._vehicle_name)
        return self._state

    def enable(self) -> None:
        """Enable API control for the drone."""
        self._client.enableApiControl(True, vehicle_name=self._vehicle_name)

    def disable(self) -> None:
        """Disable API control for the drone."""
        self._client.enableApiControl(False, vehicle_name=self._vehicle_name)

    def arm(self) -> None:
        """Arm the drone."""
        self._client.armDisarm(True, vehicle_name=self._vehicle_name)

    def disarm(self) -> None:
        """Disarm the drone."""
        self._client.armDisarm(False, vehicle_name=self._vehicle_name)
