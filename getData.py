#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import csv
import sys
import time
import re
import shutil
import zipfile
try:
    import py7zlib
except ImportError:
    # 7zip not enabled
    print "Pylzma module not enable. 7zip can't be used."

# Use modified gsconfig module from libs directory 
import libs.geoserver.catalog
import libs.geoserver.util
from libs import requests
    
# Get color for screen printing
class bcolors:
    HEADER = '\033[95m'  # rose
    OKBLUE = '\033[94m'  # blue
    OKGREEN = '\033[92m'  # green
    WARNING = '\033[93m'  # orange
    FAIL = '\033[91m'  # red
    ENDC = '\033[0m'  # end line
    BOLD = '\033[1m'  # bold ?
    UNDERLINE = '\033[4m'  # highlight

def unzip(filezip=None, pathdst='', remove_zip=False):
    if os.path.isfile(filezip):
        if pathdst == '': pathdst = os.getcwd()  # # on dezippe dans le repertoire locale
        with zipfile.ZipFile(filezip, 'r') as zfile:
            print "Files unzip from archive:"
            for i in zfile.namelist():  # # On parcourt l'ensemble des fichiers de l'archive 
                print '- ' + i 
                if os.path.isdir(i):  # # S'il s'agit d'un repertoire, on se contente de creer le dossier 
                    try: os.makedirs(pathdst + os.sep + i) 
                    except: pass 
                else: 
                    try: os.makedirs(pathdst + os.sep + os.path.dirname(i)) 
                    except: pass 
                    data = zfile.read(i)  # # lecture du fichier compresse 
                    fp = open(pathdst + os.sep + i, "wb")  # # creation en local du nouveau fichier 
                    fp.write(data)  # # ajout des donnees du fichier compresse dans le fichier local 
                    fp.close()
        if remove_zip: os.remove(filezip)
        return True
    return False
  
def un7zip(filezip, pathdst=''): 
    if pathdst == '': pathdst = os.getcwd()  # # on dezippe dans le repertoire locale 
    with open(filezip, 'rb') as fp:
        archive = py7zlib.Archive7z(fp)
        for name in archive.getnames():
            outfilename = os.path.join(pathdst, name)
            outdir = os.path.dirname(outfilename)
            if not os.path.exists(outdir):
                os.makedirs(outdir)
            outfile = open(outfilename, 'wb')
            outfile.write(archive.getmember(name).read())
            outfile.close()

def getUnzipFile(url = False, tmp_dir = False):
    print('Get and unzip ' + url + ' file in ' + tmp_dir + '.')
    if url:
        dirname, basename = os.path.split(url)
        filename, ext = os.path.splitext(basename)

        if tmp_dir and ext in ['.zip', '.7zip']:
            tmp_data_dir = os.path.join(tmp_dir, filename)
            tmp_data_file = os.path.join(tmp_data_dir, basename)

            # Create tmp directory to get layer data zip
            if not os.path.exists(tmp_data_dir):
                os.makedirs(tmp_data_dir)
            
            # Get and copy zip file
            if url.startswith('http'):
                # Remote zip file
                print "Get remote ZIP files."
                response = requests.get(url, stream=True)
                with open(tmp_data_file, 'wb') as out_file:
                    shutil.copyfileobj(response.raw, out_file)
                del response
            else:
                # Local zip file
                print "Get local ZIP files."
                shutil.copy(url, tmp_data_file)
                
            #Unzip file according to zip extension
            if ext == '.zip':
                unzip(tmp_data_file, tmp_data_dir, True)
            elif ext == '.7z':
                un7zip(tmp_data_file, tmp_data_dir)
            else:
                print "Error: can't open and unzip file."
            
            return os.path.join(tmp_data_dir, filename)
    
    return False

def createStyle(row, sld_file):
    #print 'Create style ' + row['STYLE_NAME'] + ' in Geoserver.'
    with open(sld_file) as sld_f:
        cat.create_style(row['STYLE_NAME'], sld_f.read(), overwrite=True)
        
def createLayer(row):
    #print 'Create layer ' + row['LAYER_NAME'] + ' or overwrite it if exists in Geoserver.'
    # Get and unzip data file
    pathfile = getUnzipFile(row['DATA_FILEZIP'], node['tmp_dir'])
    # If pathfile exists (zip file has been unzip)
    if pathfile:
        # Add style to Geoserver
        if os.path.isfile(pathfile + '.sld'):
            print 'Create style ' + row['STYLE_NAME'] + ' in Geoserver.'
            createStyle(row, pathfile + '.sld')
        # Add layer to Geoserver
        data = libs.geoserver.util.shapefile_and_friends(pathfile)
        print 'Create or overwrite data layer ' + row['LAYER_NAME'] + ' in Geoserver.'
        ft = cat.create_featurestore(name=row['LAYER_NAME'], data=data, workspace=ws, overwrite=True)
    # Update layer info
    print 'Update metadata layer ' + row['LAYER_NAME'] + ' in Geoserver.'
    updateLayer(row)

def updateLayer(row):
    #print 'Update metadata layer ' + row['LAYER_NAME'] + ' in Geoserver.'
    # Update layer info
    layer = cat.get_layer(row['LAYER_NAME'])
    layer.default_style = row['STYLE_NAME'].encode('utf-8')
    layer.attribution = { 'title': row['ATTRIBUTION_TITLE'],
                          'href': row['ATTRIBUTION_HREF'],
                          'height': row['ATTRIBUTION_LOGO_HEIGHT'],
                          'width': row['ATTRIBUTION_LOGO_WIDTH'],
                          'type': row['ATTRIBUTION_LOGO_TYPE'],
                          'url': row['ATTRIBUTION_LOGO_URL'] }
    cat.save(layer)
    # Update layer resource info
    resource = layer.resource
    resource.title = row['RESSOURCE_TITLE'].decode('utf-8')
    resource.abstract = row['RESSOURCE_ABSTRACT'].encode('utf-8')
    keywords = []
    if row['RESSOURCE_KEYWORDS']:
        for keyword in row['RESSOURCE_KEYWORDS'].split(','):
            keywords.append(keyword.strip().encode('utf-8'))
    resource.keywords = keywords
    metadata_links = []
    if row['MD_FILEID']:
        for md_link in md_links: 
            metadata_links.append((md_link[0], md_link[1], md_link[2] + row['MD_FILEID']))
    resource.metadata_links = metadata_links
    cat.save(resource)

def deleteLayer(row):
    #print 'Delete layer ' + row['LAYER_NAME'] + ' from Geoserver.'
    layer = cat.get_layer(row['LAYER_NAME'])
    cat.delete(layer)
    cat.reload()
    store = cat.get_store(row['LAYER_NAME'])
    cat.delete(store)
    cat.reload()

# Geonetwork URL to get XML file
gn_url = "https://www.cigalsace.org/geonetwork/apps/georchestra/?uuid="

md_links =  [
                ('text/html', 'TC211', 'https://www.cigalsace.org/geonetwork/apps/georchestra/?uuid='),
                ('text/xml', 'TC211', 'https://www.cigalsace.org/geonetwork/srv/fre/xml_iso19139?uuid='),
                ('text/html', 'ISO19115:2003', 'https://www.cigalsace.org/geonetwork/apps/georchestra/?uuid='),
                ('text/xml', 'ISO19115:2003', 'https://www.cigalsace.org/geonetwork/srv/fre/xml_iso19139?uuid=')
            ]

# Directory of nodes files
nodes_dir = 'nodes'
# Get list of nodes files
files = [ f for f in os.listdir(nodes_dir) if os.path.isfile(os.path.join(nodes_dir, f)) ]

count_file = 1
for file in files:
    print ''
    print bcolors.OKGREEN + u'*' * 80 + bcolors.ENDC
    print bcolors.OKGREEN + u'File ' + str(count_file) + '/' + str(len(files)) + ': ' + file + '.' + bcolors.ENDC
    if file.startswith('_'):
        print u'Fichier ignoré.'
    else:
        file_path = os.path.join(nodes_dir, file)
        with open(file_path, 'r') as json_data:
            data = json.load(json_data)

        print bcolors.BOLD + u'Organisme: ' + data['organisme'] + bcolors.ENDC
        
        count_node = 1
        for node in data['nodes']:
            print ''
            print bcolors.OKBLUE + u'-' * 80 + bcolors.ENDC
            print bcolors.OKBLUE + u'Node ' + str(count_node) + '/' + str(len(data['nodes'])) + bcolors.ENDC
            print u'Description: ' + node['description']
            if node['active'] == '0':
                print u'Noeud désactivé.'
            else:
                print u'Active: ' + node['active']
                print u'CSV file: ' + os.path.join(node['src_csv_path'], node['src_csv_file'])
                print u'Temp directory: ' + node['tmp_dir']
                
                # Connexion to Geoserver
                cat = libs.geoserver.catalog.Catalog(node['gs_url'] + 'rest', node['gs_login'], node['gs_pwd'])
                ws = cat.get_workspace (node['gs_workspace'])
                if ws is None:
                    ws = cat.create_workspace(node['gs_workspace'], node['gs_url'] + node['gs_workspace'])
                
                # Full path to CSV file
                csv_filepath = os.path.join(node['tmp_dir'], node['src_csv_file'])
                # Full path to CSV temp file
                tmp_csv_file = 'tmp_' + node['src_csv_file']
                tmp_csv_filepath = os.path.join(node['tmp_dir'], tmp_csv_file)
                
                # Create tmp_dir
                if not os.path.isdir(node['tmp_dir']):
                    os.makedirs(node['tmp_dir'])
                
                print u'Start: ' + str(time.strftime("%Y-%m-%d %H:%M:%S"))
                # Check if use local CSV file or HTTP URL
                if node['src_csv_path'].startswith('http'):
                    r = requests.get(node['src_csv_path'] + node['src_csv_file'])
                    # Save CSV file in temp directory
                    with open(csv_filepath, 'w') as file:
                        file.write(r.text.encode('iso-8859-1'))
                else:
                    # Copy CSV file to tmp directory
                    shutil.copy(os.path.join(node['src_csv_path'], node['src_csv_file']), csv_filepath) 
                
                # Read CSV saved file
                file = open(csv_filepath, 'rt')
                reader = csv.DictReader(file)
                
                if not os.path.isfile(tmp_csv_filepath):
                    # First harvesting for this node
                    for row in reader:
                        print 'Create layer ' + row['LAYER_NAME'] + ' or overwrite it if exists in Geoserver.'
                        createLayer(row)
                else:
                    # Define var
                    layers = {}
                    tmp_layers = {}
                    del_layers = {}
                    
                    # Read CSV tmp file
                    tmp_file = open(tmp_csv_filepath, 'rt')
                    tmp_reader = csv.DictReader(tmp_file)
                    
                    # Init tmp and del layers
                    for tmp_row in tmp_reader:
                        tmp_layers[tmp_row['LAYER_NAME']] = tmp_row
                        del_layers[tmp_row['LAYER_NAME']] = tmp_row
                    # Init layers
                    for row in reader:
                        layers[row['LAYER_NAME']] = row

                    for layer_name, row in layers.items():
                        add = True
                        for tmp_layer_name, tmp_row in tmp_layers.items():
                            if layer_name == tmp_layer_name:
                                # Layer exists in tmp_file: not need to create or delete
                                add = False
                                del del_layers[layer_name]
                                if row['DATE'] != tmp_row['DATE']:
                                    # Update layer => data + metadata = create layer with overwrite
                                    print 'Update layer ' + row['LAYER_NAME'] + ': overwrite data and metadata.'
                                    #updateLayer(row)
                                    createLayer(row)                                    
                                else:
                                    print "Layer not modified."
                        if add:
                            # layer is in reader but not in tmp_reader
                            print 'Create layer ' + row['LAYER_NAME'] + ' or overwrite it if exists in Geoserver.'
                            createLayer(row)
                    
                    # Delete layers of del_layers dictionary
                    for del_layer_name, del_row in del_layers.items():
                        print 'Delete layer ' + row['LAYER_NAME'] + '.'
                        deleteLayer(del_row)
                        
                    tmp_file.close()
                    
                file.close()
                
                # Copy CSV file to tmp file
                shutil.copy(csv_filepath, tmp_csv_filepath) 
                
                print u'End: ' + str(time.strftime("%Y-%m-%d %H:%M:%S"))

                count_node += 1
                
        count_file += 1

