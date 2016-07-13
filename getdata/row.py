#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""row.py module
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
# Load getdata module
import helpers
from config import log
from config import config
# Load gsconfig module
try:
    import geoserver.catalog
    import geoserver.util
except ImportError:
    # gsconfig not enabled
    print "gsconfig module not enable. Geoserver can't be used."


class Row(object):
    """Class to define config object from config files"""

    def __init__(self, row={}, columns={}):
        """Init Row object

        :param row: set of a row values get from CSV file
        :type row: dictionary
        :param columns: list of columns name mapping
        :type columns: dictionary

        Use of Row() object::

        >>> # Utilisation de la class ROW()
        >>> csv_row = {}  # dict recup du fichier CSV
        >>> columns_section = config['MAIN']['columns_section']
        >>> row = Row(csv_row, config[columns_section])

        """
        self.initColumns(row, columns)

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

    def initColumns(self, row=None, columns=None):
        """Init columns attributes of row object

        :param row: set of a row values get from CSV file
        :type row: dictionary
        :param columns: list of columns name mapping
        :type columns: dictionary

        """
        if columns:
            self.columns = columns
        if row:
            self.row = row
        for key, value in self.columns.items():
            if value not in self.row:
                self.row[value] = ''
            setattr(self, key, self.row[value].decode('utf-8'))

    def createLayer(self, tmp_dir=None, cat=None, ws=None):
        """Create a layer from row values

        :param tmp_dir: tmp_dir to unzip file and get data
        :type tmp_dir: string
        :param cat: geoserver catalog object of gs-config
        :type cat: object
        :param ws: geoserver workspace object of gs-config
        :type ws: object
        :return: True or False
        :rtype: boolean

        """
        if self.layer_name and tmp_dir and cat:
            # Get and unzip data file of DATA_FILEZIP CSV column
            pathfile = helpers.getUnzipFile(self.data_filezip, tmp_dir, True)
            # If pathfile exists (zip file has been unzip)
            if pathfile:
                # Create style to Geoserver if necessary or overwrite it
                if self.style_name and os.path.isfile(self.sld_file):
                    log.log('Create style ' + self.style_name + ' in Geoserver.', 'INFO', 0)
                    Style(self.style_name, self.sld_file).createStyle(cat)
                # Add layer to Geoserver
                log.log('Create or overwrite data layer ' + self.layer_name + ' in Geoserver.', 'INFO', 0)
                data = geoserver.util.shapefile_and_friends(pathfile)
                cat.create_featurestore(name=self.layer_name, data=data, workspace=ws, overwrite=True)
            # Update layer info
            log.log('Update metadata layer ' + self.layer_name + ' in Geoserver.', 'INFO', 0)
            self.updateLayer(cat, ws)
            return True
        return False

    def updateLayer(self, cat=None, ws=None):
        """Update layer infos from row values

        :param cat: geoserver catalog object of gs-config
        :type cat: object
        :param ws: geoserver workspace object of gs-config
        :type ws: object
        :return: True or False
        :rtype: boolean

        """
        if self.layer_name and cat:
            # Update layer info
            layer = cat.get_layer(self.layer_name)
            layer.default_style = self.style_name
            layer.attribution = {'title': self.attribution_title,
                                 'href': self.attribution_href,
                                 'height': self.attribution_logo_height,
                                 'width': self.attribution_logo_width,
                                 'type': self.attribution_logo_type,
                                 'url': self.attribution_logo_url}
            cat.save(layer)
            # Update layer resource info
            # resource = layer.resource  # Too long
            resource = cat.get_resource(self.layer_name, workspace=ws)
            resource.title = self.ressource_title
            resource.abstract = self.ressource_abstract
            keywords = []
            if self.ressource_keywords:
                for keyword in self.ressource_keywords.split(','):
                    keywords.append(keyword.strip())
            resource.keywords = keywords
            metadata_links = []
            if self.md_fileid:
                if self.md_fileid.startswith('http'):
                    metadata_links.append((config['MAIN']['md_external_links'][0], config['MAIN']['md_external_links'][1], self.md_fileid))
                else:
                    for md_link in config['MAIN']['md_georchestra_links']:
                        metadata_links.append((md_link[0], md_link[1], md_link[2] + self.md_fileid))
            resource.metadata_links = metadata_links
            cat.save(resource)
            return True
        return False

    def deleteLayer(self, cat=None):
        """Delete layer infos from row values

        :param cat: geoserver catalog object of gs-config
        :type cat: object
        :return: True or False
        :rtype: boolean

        """
        if self.layer_name and cat:
            layer = cat.get_layer(self.layer_name)
            cat.delete(layer)
            cat.reload()
            store = cat.get_store(self.layer_name)
            cat.delete(store)
            cat.reload()
            return True
        return False

    def getXml(self, dst_dir=None):
        """Get XML file from row values and copy to xml_dir

        :param dst_dir: xml_dir to copy XML file
        :type dst_dir: string
        :return: True or False
        :rtype: boolean

        """
        if self.md_file and dst_dir:
            dst_file = os.path.join(dst_dir, os.path.basename(self.md_file))
            helpers.getFile(self.md_file, dst_file)

    def putXml(self, sftp, local_dir=None, dst_dir=None):
        """Send XML file from row values to remote server with SFTP

        :param local_dir: local directory as source of XML file
        :type local_dir: string
        :param dst_dir: directory to copy XML file
        :type dst_dir: string
        :return: True or False
        :rtype: boolean

        """
        if self.md_file and local_dir and dst_dir:
            src_file = os.path.join(local_dir, os.path.basename(self.md_file))
            helpers.putFile(sftp, src_file, dst_dir)


class Style(object):
    """Class to define config object from config files"""

    def __init__(self, style_name=None, sld_file=None):
        """Init config

        :param layer: set of a row values get from CSV file
        :type layer: dictionary

        """
        self.style_name = style_name
        self.sld_file = sld_file

    def createStyle(self, cat=None):
        """Create style in Geoserver

        :param cat: geoserver catalog object of gs-config
        :type cat: object
        :return: True or False
        :rtype: boolean

        """
        if self.style_name and os.path.isfile(self.sld_file):
            with open(self.sld_file) as sld_f:
                cat.create_style(self.style_name, sld_f.read(), overwrite=True)
            return True
        return False
