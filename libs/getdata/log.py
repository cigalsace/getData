#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""log.py module
"""

__author__ = "Guillaume Ryckelynck"
__copyright__ = "Copyright 2015, Guillaume Ryckelynck"
__credits__ = ["Guillaume Ryckelynck"]
__license__ = "MIT"
__version__ = "0.02"
__maintainer__ = "Guillaume Ryckelynck"
__email__ = "guillaume.ryckelynck@region-alsace.org"
__status__ = "Developement"

import time


class Log(object):
    """Log class"""

    def __init__(self, file=None, verbose=False):
        """Initialize Log object

        :param file: full filename (with path) to log
        :type file: string
        :param verbose: full filename (with path) to log
        :type verbose: string

        """
        self.file = file
        self.verbose = verbose
        self.status = ['INFO', 'WARNING', 'BUG', 'ALERT', 'URGENT']

    def setAttr(self, key=None, value=None):
        """Set attribute value for object

        :param key: key name of attribute
        :type key: string
        :param value: value of attribute
        :type value: string
        :return: value of attribute
        :rtype: string

        """
        if key:
            setattr(self, key, value)
        return value

    def getAttr(self, key=None, default=None):
        """Get attribute value of object

        :param key: key name of attribute
        :type key: string
        :param default: default value to return if attribute doesn't exist
        :type default: string
        :return: value of attribute or default value
        :rtype: string

        """
        if key and hasattr(self, key):
            return getattr(self, key, default)
        else:
            return default

    def log(self, message='', status=None, code=0, verbose=False):
        """Log a message

        :param status: status of message
        :type status: string
        :param message: message to log
        :type status: string
        :returns: log line add to file
        :rtype: string

        """
        # Get timestamp
        timestamp = int(time.time())
        # Get date and hour
        datetime = time.strftime("%Y-%m-%d %H:%M:%S")
        # Get status
        if status is None:
            status = self.status[0]
        # Log line to file
        log_line = '\t'.join([str(timestamp), str(datetime), str(status), str(code), str(message) + '\n'])
        with open(self.file, 'a') as file:
            file.write(log_line)
        if self.verbose:
            print(message)
        return log_line
