#!/bin/python3
#Copyright © 2018 Victor Oliveira <victor.oliveira@gmx.com>
#This work is free. You can redistribute it and/or modify it under the
#terms of the Do What The Fuck You Want To Public License, Version 2,
#as published by Sam Hocevar. See the COPYING file for more details.

import argparse
from urllib import request
from os import path

OUI_URL = 'http://standards-oui.ieee.org/oui.txt'
OUI_FILE = path.expanduser('~/.oui.txt')

def _downloadOUI():
    '''Download OUI file'''
    req = request.urlopen(OUI_URL)
    print('Please wait\nDownloading OUI file...')
    txt = req.read().decode()
    with open(OUI_FILE, 'w') as file:
        file.write(txt)

def CheckOUIFile():
    '''Check if OUI file exists'''
    if not path.isfile(OUI_FILE):
        _downloadOUI()

def _macStrip(mac):
    '''Remove symbols from mac address'''
    len_mac = len(mac)
    if ':' in mac:
        mac = ''.join(mac.split(':'))
    elif '-' in mac:
        mac = ''.join(mac.split('-'))
    return mac

def _macFormatter(mac):
    '''Format MAC into right format'''
    mac = ':'.join(mac[i:i+2] for i in range(0,12,2))
    return mac

def MacVerify(mac):
    '''Verify if mac contains insufucient or no hex chars'''
    mac = _macStrip(mac)
    len_mac = len(mac)
    if len_mac < 6 or len_mac > 12:
        raise ValueError('Invalid MAC address')
    try:
        int(mac, 16)
    except ValueError:
        raise ValueError('Invalid MAC address')
    return mac

def MacSearch(mac):
    mac_split = mac[:6]
    with open(OUI_FILE) as file:
        while True:
            line = file.readline()
            if line:
                if mac_split.upper() in line:
                    mac_prefix = line.split()[0]
                    mac_vendor = line.split('\t')[-1]
                    mac_vendor = mac_vendor.strip('\n')
                    return mac_vendor
            else:
                return None
                break

def MacLookup(mac):
    mac = MacVerify(mac)
    mac_original = _macFormatter(mac)
    mac_vendor = MacSearch(mac)
    if mac_vendor:
        print('{} - {}'.format(mac_original.upper(), mac_vendor))

args = argparse.ArgumentParser()
group = args.add_mutually_exclusive_group()
group.add_argument('-m',
                    '--mac',
                    help='MAC address for vendor lookup')
group.add_argument('-f',
                  '--file',
                  help='File containing MAC addresses (per line)',
                  type=argparse.FileType())
args.add_argument('-r',
                  '--repair',
                  help='Repair OUI file',
                  action='store_true')
args = args.parse_args()

if args.repair:
    _downloadOUI()

CheckOUIFile()

if args.file:
    while True:
        mac = args.file.readline()
        mac = mac.strip('\n')
        if mac:
            try:
                MacLookup(mac)
            except:
                print('{} - Invalid MAC address'.format(mac))
                pass
        else:
            break

elif args.mac:
    try:
        MacLookup(args.mac)
    except ValueError:
        print('{} - Invalid MAC address'.format(args.mac))