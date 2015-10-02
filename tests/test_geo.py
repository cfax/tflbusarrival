from geo import Geo, PostcodeMalformedError, PostcodeNotFoundError
from main import app
from flask import url_for
from functools import wraps
from mock import patch, mock_open
from nose.tools import assert_equal, assert_almost_equal, assert_raises
import os
import re

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
    """Collect all tests related to 'getEastingAndNorthing' method"""

    def __init__(self):
        self.valid_entry_one_letter = \
            '"N9  9ZW",10,534152,193613,"E92000001","E19000003","E18000007","","E09000010","E05000197"\r\n'
        self.valid_entry_two_letters = \
            '"SE9 9DE",10,542733,174310,"E92000001","E19000003","E18000007","","E09000011","E05000219"\r\n'

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
            'abc12',          # three leading letters
            '12',             # no leading letters
            '',               # empty postcode
            '__21ks',         # non-alphabetic character
            'Q22 1AB',        # Q cannot be in first place
            'AJ89 1AB',       # J cannot be in second place
            'P6V 9AB',        # V cannot be in third place
            'UW9C 2XX',       # C cannot be in fourth place
            'R7H 5IB',        # I cannot be in inward code
            'R7H 5BC',        # C cannot be in inward code
            'Z223 1AB',       # cannot have 3 numbers in outward code
            'YZ2N AB',        # cannot have 0 numbers in outward code
            'YZ2N 12AB',      # cannot have 2 numbers in outward code
            'N1 1AAX',        # correct postcode, but wrong trailing character
            'XNN1 1AA',       # correct postcode, but wrong leading character
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
            ('', 'n11nn'),                               # empty file
            ([self.valid_entry_one_letter], 'n11nn'),    # completely different postcode
            ([self.valid_entry_one_letter], 'n99zz'),    # partially matching postcode
        ):
            yield self.check_postcode_not_found, file_content, postcode

    @flask_context
    def check_postcode_found(self, postcode, expected_result):
        self.m.return_value = [self.valid_entry_one_letter, self.valid_entry_two_letters]
        with patch('geo.open', self.m, create=True):
            g = Geo()
            e, n = g.getEastingAndNorthing(postcode)
            assert_equal((e, n), expected_result)

        postcode_dir = url_for('static', filename='postcodes')
        filename = re.match('([a-z]{1,2})[0-9]', postcode.replace(' ', '')).group(1)
        filename = os.path.join(postcode_dir, filename + '.csv')
        self.m.assert_called_once_with(filename)

    def test_postcode_found(self):
        """Test that postcodes that have entries in the DB are found"""
        _, _, one_E, one_N, _ = self.valid_entry_one_letter.split(',', 4)
        _, _, two_E, two_N, _ = self.valid_entry_two_letters.split(',', 4)

        for postcode, result in (
            ('n99zw',         (one_E, one_N)),    # one leading letter, no spaces
            ('n9 9zw',        (one_E, one_N)),    # one leading letter, one space
            ('n9  9zw',       (one_E, one_N)),    # one leading letter, two spaces
            ('n  9  9  z  w', (one_E, one_N)),    # one leading letter, a few spaces
            ('se99de',        (two_E, two_N)),    # two leading letters, no spaces
            ('se9 9de',       (two_E, two_N)),    # two leading letters, one space
            ('s e99d e',      (two_E, two_N)),    # two leading letters, a few spaces
        ):
            yield self.check_postcode_found, postcode, result
