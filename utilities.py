# Collect any useful function to keep code terse and and readable

import os
import time
from urllib2 import urlopen, URLError


class Utilities(object):
    """Collection of static methods to improve code readability"""

    @staticmethod
    def url_open(url, error_msg):
        """Open the url and return the response. On failure, return the error message."""
        try:
            response = urlopen(url, data=None, timeout=10)
        except URLError:
            return error_msg

        return response

    @staticmethod
    def epoch_to_localtime(seconds):
        """Given the time in seconds since the epoch as string, return struct_time object"""
        os.environ['TZ'] = 'Europe/London'
        time.tzset()
        return time.localtime(int(seconds)/1000)

    @staticmethod
    def format_time(time_struct):
        return time.strftime('%H:%M:%S', time_struct)
