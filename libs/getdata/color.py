#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""color.py module
"""

__author__ = "Guillaume Ryckelynck"
__copyright__ = "Copyright 2015, Guillaume Ryckelynck"
__credits__ = ["Guillaume Ryckelynck"]
__license__ = "MIT"
__version__ = "0.02"
__maintainer__ = "Guillaume Ryckelynck"
__email__ = "guillaume.ryckelynck@region-alsace.org"
__status__ = "Developement"


class Color(object):
    """Get color for screen printing
    """
    def __init__(self):
        """Get color for screen printing
        """
        self.HEADER = '\033[95m'     # rose
        self.OKBLUE = '\033[94m'     # blue
        self.OKGREEN = '\033[92m'    # green
        self.WARNING = '\033[93m'    # orange
        self.FAIL = '\033[91m'       # red
        self.ENDC = '\033[0m'        # end line
        self.BOLD = '\033[1m'        # bold ?
        self.UNDERLINE = '\033[4m'   # highlight
