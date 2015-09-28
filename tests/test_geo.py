from geo import Geo

from nose.tools import assert_almost_equal

def test_getLatitudeAndLongitude():
    sut = Geo()
    lat, lon = sut.getLatitudeAndLongitude(313177.270, 651409.903)
    assert_almost_equal(lat, 52.65757, 5)
    assert_almost_equal(lon, 1.717922, 6)

