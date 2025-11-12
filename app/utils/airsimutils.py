"""TODO: Add module docstring."""

from __future__ import annotations

from collections.abc import Coroutine
from logging import info
from queue import Queue
from threading import Event, Thread
import time

from cosysairsim import (
    DrivetrainType,
    ImageRequest,
    ImageType,
    MultirotorClient,
    MultirotorState,
    YawMode,
)
from msgpackrpc.session import Future
import pymap3d as pm
from pyproj import Geod

from app.models.drone import DroneStatus
from app.models.order import Order, OrderStatus
from app.services.controller.drone_service import update_drone
from app.services.controller.order_service import update_order

_WGS84 = Geod(ellps="WGS84")
# _loop = asyncio.new_event_loop()
# _loop.run_forever()
_client: MultirotorClient | None = None
finished = {}
# Original Geopoint
ORIGIN_LAT, ORIGIN_LON, ORIGIN_ALT = 37.61059, 127.04397, 30

# AirSim Image Request Configuration
url = "http://localhost:8080/realtime/drone"
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
    _client.enableApiControl(True)

    info("cosysairsim client connected.")


def is_conneted() -> bool:
    return _client is not None


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
        except:
            raise

    return retval


def sim_reset():
    from os import scandir, unlink
    from shutil import rmtree

    _client.reset()
    if _client.isRecording:
        _client.stopRecording()

    with scandir(r"C:\Users\ManticoreXL\Documents\AirSim") as it:
        for entry in it:
            if entry.is_file(follow_symlinks=False) or entry.is_symlink():
                unlink(entry.path)  # 파일/심볼릭 링크 삭제
            elif entry.is_dir(follow_symlinks=False):
                rmtree(entry.path)  # 비어있지 않은 디렉토리도 재귀적으로 삭제

    _client.startRecording()


class Drone:
    """Class representing a drone in the AirSim simulation."""

    _vehicle_name: str
    _db_drone_id: int | None
    _client: MultirotorClient
    _state: MultirotorState
    _dstate: DroneStatus
    _orders: Queue[Order | None]
    _current_order: Order | None

    ### MP Drone Worker ###
    _worker: Coroutine | None
    _stop_event: Event | None
    _stop_post_event: Event | None
    _is_moving: bool
    _target: tuple[float, float, float]

    _moving_time: float

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
        self._orders = Queue()
        self._current_order = None
        _client.enableApiControl(True, vehicle_name=self._vehicle_name)
        self._dstate = DroneStatus.IDLE
        self._db_drone_id = None
        self._is_moving = False
        self._moving_time = 0
        self._original = (0, 0, 0)

    @property
    def vehicle_name(self) -> str:
        """Get the vehicle name of the drone."""
        return self._vehicle_name

    @property
    def state(self) -> MultirotorState:
        """Get the current state of the drone."""
        return self._state

    @property
    def dstate(self) -> DroneStatus:
        """Get the current DroneStatus of the drone."""
        return self._dstate

    @property
    def id(self) -> int | None:
        """Get a unique identifier for the drone instance."""
        return self._db_drone_id

    def set_db_drone_id(self, db_drone_id: int) -> None:
        """Set the database drone ID for the drone instance."""
        self._db_drone_id = db_drone_id

    def update_state(self) -> MultirotorState:
        """Update and return the current state of the drone.

        :return: The current state of the drone.
        """
        self._state = self._client.getMultirotorState(vehicle_name=self._vehicle_name)

        if self.id is not None:
            update_drone(
                drone_id=self.id,
                status=self._dstate,
                cur_lat=self._state.gps_location.latitude,
                cur_lon=self._state.gps_location.longitude,
                cur_alt=self._state.gps_location.altitude,
            )
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
        # # TODO: Improve dispatch logic
        # order.drone_id = self.id
        # order.order_status = OrderStatus.ACCEPTED
        # self._orders.put(order)
        # self._dstate = DroneStatus.DELIVERING
        # update_order(order.order_id, order)
        # self.update_state()

        def pickup(order: Order) -> None:
            self._takeoff()
            # self._dstate = DroneStatus.DELIVERING
            self.update_state()
            self._go_to_position(
                self.state.gps_location.latitude, self.state.gps_location.longitude, 200, move=False
            )
            self.update_state()
            self._go_to_position(order.receive_lat, order.receive_lon, 500)
            # self._go_to_position(37.623662, 127.061441, 300)  # 이마트 트레이더스 월계점
            self.update_state()
            self._go_to_position(order.receive_lat, order.receive_lon, 50, move=False)
            # self._go_to_position(37.623662, 127.061441, 35)
            update_order(order.order_id, self.current_order)
            self._land()
            self.update_state()

        def deliver(order: Order) -> None:
            self._takeoff()
            self.update_state()
            self._go_to_position(
                self.state.gps_location.latitude, self.state.gps_location.longitude, 200, move=False
            )
            self.update_state()
            self._go_to_position(order.deliver_lat, order.deliver_lon, 500)
            # self._go_to_position(37.620264, 127.056199, 300)  # 광운고등학교 운동장
            self.update_state()
            self._go_to_position(order.deliver_lat, order.deliver_lon, 50, move=False)
            # self._go_to_position(37.620264, 127.056199, 35)
            self._land()
            self.current_order.order_status = OrderStatus.DELIVERED
            update_order(order.order_id, self.current_order)
            self.update_state()

        def returntostation() -> None:
            self._takeoff()
            self.update_state()
            self._go_to_position(
                self.state.gps_location.latitude, self.state.gps_location.longitude, 200, move=False
            )
            self.update_state()
            self._go_to_position(ORIGIN_LAT, ORIGIN_LON, 500)
            self.update_state()
            self._go_to_position(ORIGIN_LAT, ORIGIN_LON, ORIGIN_ALT, 35, move=False)
            self._land()

            self.update_state()

        self._current_order = order
        self._is_moving = False
        self._client.enableApiControl(True, self.vehicle_name)
        self.arm()

        self.current_order.order_status = OrderStatus.ACCEPTED
        update_order(order.order_id, order)
        self.update_state()

        # Takeoff
        # Go to pickup location
        pickup(order)

        # Go to delivery location
        deliver(order)

        self._dstate = DroneStatus.IDLE
        self.update_state()
        returntostation()
        self.disarm()

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
        if self._worker:
            self._orders.put(None)  # Unblock the queue if waiting
            self._worker

    ### Drone commands ###
    def _takeoff(self) -> Future:
        """Command the drone to take off."""
        return self._client.takeoffAsync(vehicle_name=self._vehicle_name).join()

    def _land(self) -> Future:
        """Command the drone to land."""
        return self._client.landAsync(vehicle_name=self._vehicle_name).join()

    def _go_to_position(
        self,
        latitude: float,
        longitude: float,
        altitude: float,
        velocity: float = 50.0,
        move: bool = True,
    ) -> None:
        """Command the drone to go to a specific position."""
        if latitude is None or longitude is None or altitude is None:
            raise ValueError("Latitude, Longitude, and Altitude must be provided.")

        e, n, u = pm.geodetic2enu(latitude, longitude, altitude, ORIGIN_LAT, ORIGIN_LON, ORIGIN_ALT)

        if move:
            self._target = (longitude, latitude, altitude)
            self._moving_time = time.time()
            self._is_moving = True

        self._client.moveToGPSAsync(
            latitude,
            longitude,
            altitude,
            velocity,
            drivetrain=DrivetrainType.ForwardOnly,
            yaw_mode=YawMode(is_rate=False, yaw_or_rate=0),
            # timeout_sec=360,
            vehicle_name=self._vehicle_name,
        ).join()

        self._is_moving = False

    def image_response(self) -> None:
        """Post drone information to a monitoring service."""
        from os import scandir
        import time

        geo_points = self.state.gps_location

        if self._is_moving:
            dt = time.time() - self._moving_time
            d_distance = 50 * dt
            az12, az21, dist = _WGS84.inv(
                self._target[0], self._target[1], geo_points.longitude, geo_points.latitude
            )
            lon, lat, back_az = _WGS84.fwd(
                geo_points.longitude, geo_points.latitude, az21, d_distance
            )
            alt = geo_points.altitude
        else:
            lat, lon, alt = (
                geo_points.latitude,
                geo_points.longitude,
                geo_points.altitude,
            )

        dir_path = None

        with scandir(r"C:\Users\ManticoreXL\Documents\AirSim") as it:
            for entry in it:
                if entry.is_dir(follow_symlinks=False):
                    dir_path = entry.path

        file_bytes = b"ERROR"

        if dir_path:
            with scandir(dir_path + r"\images") as it:
                files = [e for e in it if e.is_file()]
                last = max(files, key=lambda e: e.name)
                print(f"image path: {last.path}")
                with open(last.path, "rb") as f:
                    file_bytes = f.read()

        data = {
            "drone_id": self.id,
            "vehicle_name": self.vehicle_name,
            "state": {
                "gps_location": {
                    "lat": lat,
                    "lon": lon,
                    "alt": alt,
                }
            },
            "current_order": self.current_order.order_id,
            "order_status": self.current_order.order_status,
        }
        if self.current_order.order_status == OrderStatus.DELIVERED:
            self._current_order = None

        return data, {"image": ("capture", file_bytes, "image/png")}
