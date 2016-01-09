#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""getData.py module

Main file of getData application.
"""

__author__ = "Guillaume Ryckelynck"
__copyright__ = "Copyright 2015, Guillaume Ryckelynck"
__credits__ = ["Guillaume Ryckelynck"]
__license__ = "MIT"
__version__ = "0.03"
__maintainer__ = "Guillaume Ryckelynck"
__email__ = "guillaume.ryckelynck@region-alsace.org"
__status__ = "Developement"


import os
import json
import csv
import time
import shutil
# Use modified gsconfig module from libs directory
import libs.geoserver.catalog
import libs.geoserver.util
# Use local requests module from libs directory
from libs.getdata import config
from libs.getdata import color
from libs.getdata import helpers
from libs.getdata import row

# Define color object
color = color.Color()


def getMetadata(node=[], reader=[]):
    """Get XML metadata files from CSV file reader

    :param node: node file configuration values
    :type node: list
    :param reader: reader of CSV file
    :type reader: list
    """
    # Manage metadata
    # Remove dst directory and recreate it (empty)
    config.log.log(u'Empty ' + node['xml_dir'] + ' directory.', 'INFO', 0)
    if os.path.isdir(node['xml_dir']):
        shutil.rmtree(node['xml_dir'])
    os.mkdir(node['xml_dir'])
    config.log.log(u'Get metadata in ' + node['xml_dir'] + ' directory.', 'INFO', 0)
    for csv_row in reader:
        r = row.Row(csv_row, config.config['COLUMNS'])
        config.log.log(u'Get metadata file: ' + r.getAttr('md_fileid'), 'INFO', 0)
        r.getXml(node['xml_dir'])


def getData(node=[], reader=[], tmp_csv_filepath=''):
    """Get data ZIP/7Z files from CSV file reader

    :param node: node file configuration values
    :type node: list
    :param reader: reader of CSV file
    :type reader: list
    :param tmp_csv_filepath: fullpath of tmp file CSV
    :type tmp_csv_filepath: string
    """
    # Connexion to Geoserver
    config.log.log(u'Connexion to Geoserver workspace ' + node['gs_workspace'], 'INFO', 0)
    cat = libs.geoserver.catalog.Catalog(node['gs_url'] + 'rest', node['gs_login'], node['gs_pwd'])
    ws = cat.get_workspace(node['gs_workspace'])
    if ws is None:
        config.log.log(u'Create workspace ' + node['gs_workspace'], 'INFO', 0)
        ws = cat.create_workspace(node['gs_workspace'], node['gs_url'] + node['gs_workspace'])
    # Manage layer creation in geoserver
    if not os.path.isfile(tmp_csv_filepath):
        # First harvesting for this node
        for csv_row in reader:
            r = row.Row(csv_row, config.config['COLUMNS'])
            config.log.log('Create layer ' + r.getAttr('layer_name') + ' or overwrite it if exists in Geoserver.', 'INFO', 0)
            r.createLayer(node['tmp_dir'], cat)
    else:
        # Read CSV tmp file
        with open(tmp_csv_filepath, 'rt') as tmp_file:
            tmp_reader = list(csv.DictReader(tmp_file))

        # Init del layers
        del_layers = []
        for csv_row_tmp in tmp_reader:
            tmp_r = row.Row(csv_row_tmp, config.config['COLUMNS'])
            del_layers.append(tmp_r.getAttr('layer_name'))

        # Manage layers
        for csv_row in reader:
            r = row.Row(csv_row, config.config['COLUMNS'])
            add = True
            for csv_row_tmp in tmp_reader:
                tmp_r = row.Row(csv_row_tmp, config.config['COLUMNS'])
                if r.getAttr('layer_name') == tmp_r.getAttr('layer_name'):
                    # Layer exists in tmp_file: not need to create it
                    add = False
                    del_layers.remove(tmp_r.getAttr('layer_name'))
                    if r.getAttr('date') != tmp_r.getAttr('date'):
                        # Update layer => data + metadata = create layer with overwrite
                        config.log.log('Update layer ' + r.getAttr('layer_name') + ': overwrite data and metadata.', 'INFO', 0)
                        r.createLayer(node['tmp_dir'], cat)
                    else:
                        config.log.log('Layer ' + r.getAttr('layer_name') + ' not modified.', 'INFO', 0)
            if add:
                # layer is in reader but not in tmp_reader
                config.log.log('Create layer ' + r.getAttr('layer_name') + ' or overwrite it if exists in Geoserver.', 'INFO', 0)
                r.createLayer(node['tmp_dir'], cat)

        for csv_row_del in del_layers:
            # Delete layers of del_layers dictionary
            del_r = row.Row(csv_row_del, config.config['COLUMNS'])
            config.log.log('Delete layer ' + del_r.getAttr('layer_name') + '.', 'INFO', 0)
            del_r.deleteLayer(cat)


def main():
    # if args.file:
    #     pass
    # else:
    # Get list of nodes files from config node_dir
    nodes_files = [f for f in os.listdir(config.config['MAIN']['nodes_dir']) if os.path.isfile(os.path.join(config.config['MAIN']['nodes_dir'], f))]

    count_file = 1
    for nodes_file in nodes_files:
        config.log.log('', 'INFO', 0)
        config.log.log(color.OKGREEN + u'*' * 80 + color.ENDC, 'INFO', 0)
        config.log.log(color.OKGREEN + u'File ' + str(count_file) + '/' + str(len(nodes_files)) + ': ' + nodes_file + '.' + color.ENDC, 'INFO', 0)
        if nodes_file.startswith('_'):
            config.log.log(u'File skipped.', 'INFO', 0)
        else:
            file_path = os.path.join(config.config['MAIN']['nodes_dir'], nodes_file)
            with open(file_path, 'r') as json_data:
                data = json.load(json_data)

            config.log.log(color.BOLD + u'Organisme: ' + data['organisme'] + color.ENDC, 'INFO', 0)

            count_node = 1
            for node in data['nodes']:
                config.log.log('', 'INFO', 0)
                config.log.log(color.OKBLUE + u'-' * 80 + color.ENDC, 'INFO', 0)
                config.log.log(color.OKBLUE + u'Node ' + str(count_node) + '/' + str(len(data['nodes'])) + color.ENDC, 'INFO', 0)
                config.log.log(u'Description: ' + node['description'], 'INFO', 0)
                if node['active'] == '0':
                    config.log.log(u'Node disabled.', 'INFO', 0)
                else:
                    # Log node informations
                    config.log.log(u'Active: ' + node['active'], 'INFO', 0)
                    config.log.log(u'CSV file: ' + os.path.join(node['src_csv_path'], node['src_csv_file']), 'INFO', 0)
                    config.log.log(u'XML directory: ' + node['xml_dir'], 'INFO', 0)
                    config.log.log(u'TMP directory: ' + node['tmp_dir'], 'INFO', 0)

                    # Full path to CSV file
                    csv_filepath = os.path.join(node['tmp_dir'], node['src_csv_file'])
                    # Full path to CSV temp file
                    tmp_csv_file = 'tmp_' + node['src_csv_file']
                    tmp_csv_filepath = os.path.join(node['tmp_dir'], tmp_csv_file)

                    # Create tmp_dir
                    if not os.path.isdir(node['tmp_dir']):
                        os.makedirs(node['tmp_dir'])

                    config.log.log(u'Start: ' + str(time.strftime("%Y-%m-%d %H:%M:%S")), 'INFO', 0)
                    # Get file from path or URL
                    helpers.getFile(os.path.join(node['src_csv_path'], node['src_csv_file']), csv_filepath)

                    # Read CSV saved file
                    with open(csv_filepath, 'rt') as csv_file:
                        reader = list(csv.DictReader(csv_file))

                    # metadata_active = 0/1
                    config.log.log(u'Metadata active: ' + config.config['MAIN']['metadata_active'], 'INFO', 0)
                    if config.config['MAIN']['metadata_active']:
                        getMetadata(node, reader)

                    config.log.log(u'Data active: ' + config.config['MAIN']['data_active'], 'INFO', 0)
                    # data_active = 0/1
                    if config.config['MAIN']['data_active']:
                        getData(node, reader, tmp_csv_filepath)

                    # Copy CSV file to tmp file
                    shutil.copy(csv_filepath, tmp_csv_filepath)

                    config.log.log(u'End: ' + str(time.strftime("%Y-%m-%d %H:%M:%S")), 'INFO', 0)

                    count_node += 1

            # nodes_file.close()
            count_file += 1


if __name__ == "__main__":
    main()
