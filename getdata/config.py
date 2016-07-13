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
import json
import log


def get_cfg(file=None):
    """Read config file and return dict

    :param file: path of JSON file to save
    :type file: string
    :returns: dictionary of config file
    :rtype: dictionary

    """
    # Parse config file and init columns var
    if file is not None and os.path.isfile(file):
        with open(file) as config_file:
            config = json.load(config_file)
        # Add some values to config var
        config['MAIN']['md_georchestra_links'] = [('text/html', 'TC211', config['MAIN']['geonetwork_html_url']), ('text/xml', 'TC211', config['MAIN']['geonetwork_xml_url']), ('text/html', 'ISO19115:2003',  config['MAIN']['geonetwork_html_url']), ('text/xml', 'ISO19115:2003', config['MAIN']['geonetwork_xml_url'])]
        config['MAIN']['md_external_links'] = ['text/html', 'TC211']
        return config
    return {}


#: Config file path
CONFIG_FILE = './config.json'

#: Init main config object: parse config file and init columns var
config = get_cfg(CONFIG_FILE)

#: Init main log object
log = log.Log(config['MAIN']['log_file'], config['MAIN']['verbose'])
