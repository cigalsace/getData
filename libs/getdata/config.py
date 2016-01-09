#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""config.py module
"""

__author__ = "Guillaume Ryckelynck"
__copyright__ = "Copyright 2015, Guillaume Ryckelynck"
__credits__ = ["Guillaume Ryckelynck"]
__license__ = "MIT"
__version__ = "0.02"
__maintainer__ = "Guillaume Ryckelynck"
__email__ = "guillaume.ryckelynck@region-alsace.org"
__status__ = "Developement"

import os
import ConfigParser
from libs.getdata import log

#: Config file path
CONFIG_FILE = '../config.cfg'


def get_cfg(file=None):
    """Read config file and return dict

    :param file: path of JSON file to save
    :type file: string
    :returns: dictionary of config file
    :rtype: dictionary

    """
    if file is not None and os.path.isfile(file):
        parser = ConfigParser.RawConfigParser()
        parser.read(file)
        config_dict = {}
        for sect in parser.sections():
            config_dict[sect] = {}
            for name, value in parser.items(sect):
                config_dict[sect][name] = value
        return config_dict
    return False


# Parse config file and init columns var
config = get_cfg(CONFIG_FILE)
# Add some values to config var
config['MAIN']['md_georchestra_links'] = [('text/html', 'TC211', config['MAIN']['geonetwork_html_url']),
                                          ('text/xml', 'TC211', config['MAIN']['geonetwork_xml_url']),
                                          ('text/html', 'ISO19115:2003', config['MAIN']['geonetwork_html_url']),
                                          ('text/xml', 'ISO19115:2003', config['MAIN']['geonetwork_xml_url'])]
config['MAIN']['md_external_links'] = ['text/html', 'TC211']

#: Init main log object
log = log.Log(config['MAIN']['log_file'], config['MAIN']['verbose'])
