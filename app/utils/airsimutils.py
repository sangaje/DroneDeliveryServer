"""TODO: Add module docstring."""

from __future__ import annotations

from logging import info
from queue import Queue
from threading import Event, Thread

from cosysairsim import ImageRequest, ImageType, MultirotorClient, MultirotorState
from msgpackrpc.session import Future

from app.models.order import Order, OrderStatus
from app.services.controller.order_service import update_order

_client: MultirotorClient | None = None

# AirSim Image Request Configuration
url = "http://localhost:8080/..."  # TODO: Replace with actual URL
_CAM = "0"
_img_reqs = [
    ImageRequest(_CAM, ImageType.Scene, pixels_as_float=False, compress=True),
]


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
    _client.confirmConnection()

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
        # TODO What exceptions can be raised here? Fuck
        except Exception:
            pass
    return retval


class Drone:
    """Class representing a drone in the AirSim simulation."""

    _vehicle_name: str
    _client: MultirotorClient
    _state: MultirotorState
    _orders: Queue[Order | None]
    _current_order: Order | None

    ### MP Drone Worker ###
    _worker: Thread | None
    _stop_event: Event | None
    _stop_post_event: Event | None

    def __init__(self, vehicle_name: str) -> None:
        """Initialize the Drone object.

        :param vehicle_name: The name of the drone in the AirSim simulation.
        """
        ### Initialize Drone attributes ###
        global _client
        self._vehicle_name = vehicle_name
        if not _client:
            raise ConnectionError(_client)
        self._client = _client
        self.update_state()
        self._orders = Queue()
        self._current_order = None

        ### Initialize Drone Worker ###
        self._worker = Thread(target=self._delivery_loop, name=self._vehicle_name, daemon=True)
        self._stop_event = Event()
        self._worker.start()

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

    def start_post_info(self) -> None:
        """Start posting drone information to a monitoring service."""
        if self._stop_post_event:
            self._stop_post_event.set()

        self._stop_post_event = Event()
        Thread(target=self._post_info_loop, args=(), daemon=True).start()

    def stop_post_info(self) -> None:
        """Stop posting drone information to a monitoring service."""
        if self._stop_post_event:
            self._stop_post_event.set()
            self._stop_post_event = None

    ### Drone operations ###
    def dispatch_order(self, order: Order) -> None:
        """Dispatch the drone to execute the given order.

        :param order: The order to be executed by the drone.
        """
        # TODO: Improve dispatch logic
        order.drone_id = self.id
        order.order_status = OrderStatus.ACCEPTED
        self._orders.put(order)
        update_order(order.order_id, order)

    @property
    def current_orders_count(self) -> int:
        """Get the number of orders currently assigned to the drone."""
        return self._orders.qsize() + (1 if self._current_order else 0)

    @property
    def current_order(self) -> Order | None:
        """Get the current order being executed by the drone."""
        return self._current_order

    @property
    def current_path(self) -> list[Order]:
        """Get the current path of the drone as a list of GPS coordinates."""
        retval = []
        with self._orders.mutex:
            if self._current_order:
                retval.append(self._current_order)
            retval.extend(list(self._orders.queue))

        return retval

    def stop(self) -> None:
        """Stop the drone worker thread."""
        if self._stop_event:
            self._stop_event.set()
        if self._worker and self._worker.is_alive():
            self._orders.put(None)  # Unblock the queue if waiting
            self._worker.join()

    ### Drone commands ###
    def _takeoff(self) -> Future:
        """Command the drone to take off."""
        return self._client.takeoffAsync(vehicle_name=self._vehicle_name)

    def _land(self) -> Future:
        """Command the drone to land."""
        return self._client.landAsync(vehicle_name=self._vehicle_name)

    def _go_to_position(
        self,
        latitude: float,
        longitude: float,
        altitude: float,
        velocity: float,
    ) -> Future:
        if latitude is None or longitude is None or altitude is None:
            msg = "Latitude, Longitude, and Altitude must be provided."
            raise ValueError(msg)
        """Command the drone to go to a specific position."""
        return self._client.moveToGPSAsync(
            latitude, longitude, altitude, velocity, vehicle_name=self._vehicle_name
        )

    ### Drone Worker methods (ex. loop ...) ###
    def _delivery_loop(self) -> None:
        """Main loop for processing orders."""

        def pickup(order: Order) -> None:
            self._takeoff().join()
            self._go_to_position(order.receive_lat, order.receive_lon, order.receive_alt).join()
            self._land().join()
            order.order_status = OrderStatus.RECEIVED
            update_order(order.order_id, order)

        def deliver(order: Order) -> None:
            self._takeoff().join()
            self._go_to_position(order.deliver_lat, order.deliver_lon, order.deliver_alt).join()
            self._land().join()
            order.order_status = OrderStatus.DELIVERED
            update_order(order.order_id, order)

        if self._stop_event is None:
            msg = "Drone worker thread not properly initialized."
            raise RuntimeError(msg)

        while not self._stop_event.is_set():
            order = self._orders.get()
            if order is None:
                self._orders.task_done()
                break

            self._current_order = order

            # Takeoff
            self.enable()
            self.arm()
            # Go to pickup location
            pickup(order)

            # Go to delivery location
            deliver(order)

            self.disarm()
            self.disable()

            self._current_order = None
            self._orders.task_done()

    def _post_info_loop(self) -> None:
        """Post drone information to a monitoring service."""
        import time

        import requests as req

        while not self._stop_post_event.is_set():
            responses = self._client.simGetImages(_img_reqs, vehicle_name=self._vehicle_name)

            if len(responses) != len(_img_reqs):
                info(f"Drone {_CAM} ({self._vehicle_name}): Error getting images")
                continue

            img = responses[0]
            stat = self.update_state()
            path = self.current_path

            if path:
                path_data: list[Order] = []
                for order in path:
                    path_data.append(
                        {
                            "order_id": order.order_id,
                            "receive": {
                                "lat": order.receive_lat,
                                "lon": order.receive_lon,
                                "alt": order.receive_alt,
                            },
                            "deliver": {
                                "lat": order.deliver_lat,
                                "lon": order.deliver_lon,
                                "alt": order.deliver_alt,
                            },
                            "status": order.order_status,
                        }
                    )

                current_order = path_data[0].order_id if path_data else None
            else:
                path_data = None
                current_order = None

            data = {
                "drone_id": self.id,
                "vehicle_name": self._vehicle_name,
                "state": {
                    "gps_location": {
                        "lat": stat.gps_location.latitude,
                        "lon": stat.gps_location.longitude,
                        "alt": stat.gps_location.altitude,
                    }
                },
                "current_order": current_order,
                "path": path_data,
            }

            r = req.post(
                url,
                data=data,
                files={"image": ("capture", img.image_data_uint8, "image/png")},
            )
            r.raise_for_status()

            time.sleep(3)
