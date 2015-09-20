# Collect any useful function to keep code terse and and readable

import time
from datetime import timedelta
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
        """Given the time in seconds since the epoch, return datetime object"""
        time.tzset('GMT')
        s = time.strftime('%d/%m/%Y %H:%M:%S', time.localtime(int(seconds)/1000))
        if time.daylight:
            s += timedelta(hours=1)
        return time.strptime(s, '%d/%m/%Y %H:%M:%S')

    @staticmethod
    def format_time(datetime_object):
        return time.strftime('%H:%M:%S', datetime_object)
