from geo import Geo
from main import app
from flask import url_for
from functools import wraps

from nose.tools import assert_equal, assert_almost_equal

def flask_context(f):
    @wraps(f)
    def wrapper():
        with app.test_request_context():
            f()
    return wrapper


@flask_context
def test_init_object_correctly():
    sut = Geo()
    assert_equal(sut.postcode_dir, url_for('static', filename='postcodes'))

@flask_context
def test_getLatitudeAndLongitude():
    sut = Geo()
    lat, lon = sut.getLatitudeAndLongitude(651409.903, 313177.270)
    assert_almost_equal(lat, 52.657570, places=6)
    assert_almost_equal(lon, 1.717922, places=6)

@flask_context
def test_getEastingAndNorthing():
    pass
