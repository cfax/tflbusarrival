from geo import Geo, PostcodeMalformedError, PostcodeNotFoundError
from main import app
from flask import url_for
from functools import wraps
from mock import patch, mock_open
from nose.tools import assert_equal, assert_almost_equal, assert_raises

def flask_context(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        with app.test_request_context():
            f(*args, **kwargs)
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


class TestGetEastingAndNorthing(object):

    def __init__(self):
        self.valid_entry = '"N9  9ZW",10,534152,193613,"E92000001","E19000003","E18000007","","E09000010","E05000197"\r\n'

    def setup(self):
        self.m = mock_open()

    @flask_context
    def check_invalid_postcode(self, postcode):
        with patch('geo.open', self.m, create=True):
            g = Geo()
            with assert_raises(PostcodeMalformedError):
                g.getEastingAndNorthing(postcode)

    def test_invalid_postcode(self):
        """An error is raised if the postcode is not valid"""
        for bad_postcode in (
            'abc12',    # three leading letters
            '12',       # no leading letters
            '',         # empty postcode
            '__21ks',   # non-alphabetic character
            'n 12ff',   # leading letter ok, space following
            'nw 12ff',  # two leading letters ok, space following
        ):
            yield self.check_invalid_postcode, bad_postcode

    @flask_context
    def check_postcode_not_found(self, file_content, postcode):
        self.m.return_value = file_content
        with patch('geo.open', self.m, create=True):
            g = Geo()
            with assert_raises(PostcodeNotFoundError):
                g.getEastingAndNorthing(postcode)

    def test_postcode_not_found(self):
        """An error is raised if the postcode cannot be found"""
        for file_content, postcode in (
            ('', 'n11nn'),                    # empty file
            ([self.valid_entry], 'n11nn'),    # completely different postcode
            ([self.valid_entry], 'n99zz'),    # partially matching postcode
        ):
            yield self.check_postcode_not_found, file_content, postcode
