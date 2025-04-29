import numpy as np
from doa_processor import calculate_doa, convert_xy_to_geo

def test_calculate_doa():
    """Test DOA calculation with sample TDOA values"""
    doa = calculate_doa(0.001, -0.002, 0.0005)
    assert isinstance(doa, (int, float))
    assert 0 <= doa <= 360  # DOA should be within valid range

def test_convert_xy_to_geo():
    """Test coordinate conversion"""
    lat, lon = convert_xy_to_geo(30.0, 50.0, 1.0, 0.0)
    assert isinstance(lat, float) and isinstance(lon, float)
