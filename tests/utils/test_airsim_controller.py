"""Test cases for AirSim controller utilities."""

import app.utils.airsim_controller as airsim_controller
import pytest


def test_lla_to_ned() -> None:
    """Test the conversion from LLA to NED coordinates."""
    origin_lat = 37.4938
    origin_lon = 127.4896
    origin_alt = 50.0
    target_lat = 37.4904
    target_lon = 127.4941
    target_alt = 60.0

    n, e, d = airsim_controller.lla_to_ned(
        origin_lat, origin_lon, origin_alt, target_lat, target_lon, target_alt
    )

    # Check if the returned values are of type float
    assert n == pytest.approx(-377.349, abs=1e-2)
    assert e == pytest.approx(397.969, abs=1e-2)
    assert d == pytest.approx(-9.976, abs=1e-2)
