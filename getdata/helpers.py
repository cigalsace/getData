#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""helpers.py module
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
import shutil
import zipfile
# Load getdata module
from config import log
# Load Pylzma module (7z)
try:
    import py7zlib
except ImportError:
    # 7zip not enabled
    print "Pylzma module not enable. 7zip can't be used."
# Load requests module
try:
    import requests
    requests.packages.urllib3.disable_warnings()
except ImportError:
    # resuests not enabled
    print "resuests module not enable."
# Load pysftp module
try:
    import pysftp
except ImportError:
    # pysftp not enabled
    print "pysftp module not enable. SFTP connexion can't be used."


def unzip(filezip=None, pathdst='', remove_zip=False):
    """Unzip a ZIP or 7Z file

    :param filezip: full filename (with path) to ZIP/7Z file
    :type filezip: string
    :param pathdst: path to directory where unzip ZIP/7Z file
    :type pathdst: string
    :param remove_zip: if True, remove ZIP/7Z file after unzip
    :type remove_zip: string
    :return: True or False
    :rtype: boolean

    """
    if os.path.isfile(filezip):
        if pathdst == '':
            pathdst = os.getcwd()
        ext = os.path.splitext(filezip)[1].lower()
        if ext == '.zip':
            # ZIP file
            with zipfile.ZipFile(filezip, 'r') as zfile:
                log.log("Files unzip from archive:", 'INFO', 0)
                for zfile_name in zfile.namelist():
                    log.log('- ' + zfile_name, 'INFO', 0)
                    zfile_fullpath = os.path.join(pathdst, zfile_name)
                    if os.path.isdir(zfile_name):
                        if not os.path.isdir(zfile_fullpath):
                            os.makedirs(zfile_fullpath)
                    else:
                        if not os.path.isdir(os.path.join(pathdst, os.path.dirname(zfile_name))):
                            os.makedirs(os.path.join(pathdst, os.path.dirname(zfile_name)))
                        data = zfile.read(zfile_name)
                        fp = open(zfile_fullpath, "wb")
                        fp.write(data)
                        fp.close()
        elif ext == '.7z':
            # 7ZIP file
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
        if remove_zip:
            # Remove ZIP/7Z file
            os.remove(filezip)
        return True
    return False


def getUnzipFile(url=False, tmp_dir=False, remove_zip=False):
    """Get and unzip a file

    :param url: URL or full filename (with path) to ZIP file
    :type url: string
    :param tmp_dir: path to directory where unzip ZIP file
    :type tmp_dir: string
    :param remove_zip: if True, remove ZIP file after unzip
    :type remove_zip: string
    :return: path to unzip files or False
    :rtype: string or boolean

    """
    log.log('Get and unzip ' + url + ' file in ' + tmp_dir + '.', 'INFO', 0)
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
                log.log("Get remote ZIP file.", 'INFO', 0)
                response = requests.get(url, stream=True, verify=False)
                with open(tmp_data_file, 'wb') as out_file:
                    shutil.copyfileobj(response.raw, out_file)
                del response
            else:
                # Local zip file
                log.log("Get local ZIP file.", 'INFO', 0)
                shutil.copy(url, tmp_data_file)
            # Unzip file (delete zip file if remove-zip is True)
            unzip(tmp_data_file, tmp_data_dir, remove_zip)
            # Return path to unzip files
            return os.path.join(tmp_data_dir, filename)
    return False


def getFile(src=None, dst=None):
    """Get local or remote file

    :param src: URL or full filename (with path) to get file (remote source)
    :type src: string
    :param dst: full filename (with path) to copy source file in local destination directory
    :type dst: string

    """
    log.log('Copy ' + src + ' to ' + dst + ' file.', 'INFO', 0)
    if src.startswith('http'):
        r = requests.get(src, verify=False)
        # Save CSV file in temp directory
        with open(dst, 'w') as dst_file:
            dst_file.write(r.text.encode('iso-8859-1'))
    else:
        # Copy CSV file to tmp directory
        shutil.copy(src, dst_file)


def delFiles(sftp=None, dst=None):
    """Put local file to remote destination using SFTP

    :param dst: path directory to delete files
    :type dst: string

    """
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None

    with pysftp.Connection(host=sftp['sftp_hostname'], port=sftp['sftp_port'], username=sftp['sftp_username'], private_key_pass=sftp['sftp_private_key_pass'], private_key=sftp['sftp_private_key'], cnopts=cnopts) as sftp:
        files = sftp.listdir(dst)
        with sftp.cd(dst):
            log.log(u'Empty SFTP directory: "' + dst + '".', 'INFO', 0)
            for file in files:
                log.log(u'Remove SFTP file: "' + file + '".', 'INFO', 0)
                sftp.remove(file)


def putFile(sftp=None, src_file=None, dst=None):
    """Put local file to remote destination using SFTP

    :param src_file: full filename (with path) of local directory (source)
    :type src_file: string
    :param dst: path directory to copy source file to destination
    :type dst: string

    """
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None

    with pysftp.Connection(host=sftp['sftp_hostname'], port=sftp['sftp_port'], username=sftp['sftp_username'], private_key_pass=sftp['sftp_private_key_pass'], private_key=sftp['sftp_private_key'], cnopts=cnopts) as sftp:
        with sftp.cd(dst):
            sftp.put(src_file)
