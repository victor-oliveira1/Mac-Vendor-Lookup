#!/usr/bin/env python3
'''
Macvendor

Library/CLI to determine the vendor of a MAC address.
* You need at least 6 chars to get the vendor.
* This library can be used as a CLI program.
* If the MAC contains more than 12 chars, less than 6 chars or
  non hexadecimal chars, an exception is raised (ValueError).
* The oui_file is needed for making use of this program, and
  can be downloaded using the "download_oui" function.

CLI Examples:
$ python3 macvendor.py 84:7b:eb:dd:ee:ff
84:7b:eb:dd:ee:ff - Dell Inc.

$ python3 macvendor.py 34-E6-D7-80-45-8F 34:e6:d7:80:45:8f 0011.9343.152e 00119343152e
34-E6-D7-80-45-8F - Dell Inc.
34:e6:d7:80:45:8f - Dell Inc.
0011.9343.152e    - Cisco Systems, Inc
00119343152e      - Cisco Systems, Inc


Library Example:
>>> import macvendor
>>> macvendor.get_vendor('84:7b:eb:dd:ee:ff')
'Dell Inc.'
'''
import urllib.request
import argparse
import os.path
import os
from sys import platform

__author__ = 'Victor Oliveira <victor.oliveira@gmx.com>'
__version__ = '1.0'

if platform == "linux" or platform == "linux2":
    # linux
    OUI_FILE = '~/.oui.txt'
elif platform == "darwin":
    # OS X
    OUI_FILE = '~/.oui.txt'
elif platform == "win32":
    # Windows...
    OUI_FILE = '~\\.oui.txt'
#OUI_FILE = '~/.oui.txt'
OUI_URL = 'http://standards-oui.ieee.org/oui.txt'
#SEPARATORS = ('-', ':')
SEPARATORS = ('-', ':', '.')
BUFFER_SIZE = 1024 * 8

def _req_oui():
    req = urllib.request.urlopen(OUI_URL, timeout=5)
    return req

def _get_oui_local_size():
    stat = os.stat(os.path.expanduser(OUI_FILE))
    size = stat.st_size
    return size

def _get_oui_remote_size():
    req = _req_oui()
    size = int(req.getheader('Content-Length'))
    return size

def download_oui(oui_file=OUI_FILE):
    req = _req_oui()
    with open(os.path.expanduser(oui_file), "wb") as file:
        while True:
            buffer = req.read(BUFFER_SIZE)
            if buffer:
                file.write(buffer)
            else:
                break

def get_vendor(mac, oui_file=OUI_FILE):
    mac_clean = mac.upper()
    for separator in SEPARATORS:
        mac_clean = ''.join(mac_clean.split(separator))

    try:
        int(mac_clean, 16)
    except ValueError:
        raise ValueError('Invalid MAC address.')

    mac_size = len(mac_clean)
    if mac_size > 12 or mac_size < 6:
        raise ValueError('Invalid MAC address.')

    with open(os.path.expanduser(oui_file), encoding="utf8") as file:
        mac_half = mac_clean[0:6]
        mac_half_upper = mac_half.upper()
        while True:
            line = file.readline()
            if line:
                if line.startswith(mac_half_upper):
                    vendor = line.strip().split('\t')[-1]
                    return vendor
            else:
                break

def _cli():
    parser = argparse.ArgumentParser(
        description='Return vendor of a MAC address.')
    parser.add_argument('mac_address',
                        nargs='+',
                        help='MAC address')
    args = parser.parse_args()
    mac = args.mac_address

    have_internet = False
    try:
        oui_remote_size = _get_oui_remote_size()
        have_internet = True
    except urllib.error.URLError:
        pass

    if os.path.isfile(os.path.expanduser(OUI_FILE)):
        if have_internet:
            oui_local_size = _get_oui_local_size()
            if oui_local_size == oui_remote_size:
                pass
            else:
                print('Newer OUI file found. Downloading.')
                download_oui()
    else:
        if have_internet:
            print('No OUI file. Downloading.')
            download_oui()
        else:
            print('No internet. Can\'t download OUI file.')
            exit(1)

    try:
        for i in mac:
            vendor = get_vendor(i.upper())
            print('{:17s} - {}'.format(i, vendor))
    except ValueError:
        print('Invalid MAC address.')

if __name__ == '__main__':
    _cli()
