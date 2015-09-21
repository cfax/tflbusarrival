from utilities import Utilities

import os
from nose.tools import assert_equal

def test_epoch_to_localtime_conversion_different_timezone():
    for timezone in (
        'Africa/Bujumbura',
        'America/Danmarkshavn',
        'America/New_York',
        'Antarctica/Vostok',
        'Asia/Srednekolymsk',
        'Europe/Rome',
        'Atlantic/Madeira',
        'Atlantic/St_Helena',
        'Australia/Tasmania',
        'Indian/Mayotte',
        'Pacific/Samoa',
        'Brazil/East',
        'Cuba',
        'Zulu',
        'Etc/GMT+9',
        'Etc/GMT-2',
        'PST8PDT',
        'Etc/Greenwich',
        'GMT+0',
        'GMT-0',
        'WET',
    ):
        yield check_epoch_to_localtime_conversion_different_timezone, timezone

def check_epoch_to_localtime_conversion_different_timezone(timezone):
    os.environ['TZ'] = timezone
    seconds = '1440000441000'  # 19/08/2015 17:07:21
    time_struct = Utilities.epoch_to_localtime(seconds)
    assert_equal(2015, time_struct.tm_year)
    assert_equal(8, time_struct.tm_mon)
    assert_equal(19, time_struct.tm_mday)
    assert_equal(17, time_struct.tm_hour)
    assert_equal(7, time_struct.tm_min)
    assert_equal(21, time_struct.tm_sec)
    assert_equal(2, time_struct.tm_wday)
    assert_equal(231, time_struct.tm_yday)
    assert_equal(1, time_struct.tm_isdst)


