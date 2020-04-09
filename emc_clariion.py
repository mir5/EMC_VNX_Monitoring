#!/usr/bin/env python

# --------------------------------
# Author: Iman Mir
# Mail: <Iman.mir@gmail.com>
#  License: GPLv3                  
# --------------------------------
import optparse
import json
import sys
from os import popen, mkdir
ID=sys.argv[1]
NAVICLI = '/opt/Navisphere/bin/naviseccli'
CRED = {'User': sys.argv[2],
        'Password': sys.argv[3],
        'Host': sys.argv[1] }
CONNECT = NAVICLI + " -User " + CRED['User'] + " -Password " + CRED['Password'] + " -Scope 0 -h " + CRED['Host'] + " "
TMP_DIR = '/tmp/'+ ID
#TMP_DIR = 'F:\EMC\script\\'


lun_items = ["RAID Type", "State", "LUN Capacity(Megabytes)"]
portstate_items = ['SP Name', 'SP Port ID', 'Link Status', 'Port Status', 'Speed Value']
storagepool_items = ['Pool Name', 'State', 'Status', 'Consumed Capacity (GBs)', 'Available Capacity (GBs)',
                     'Percent Full', 'Total Subscribed Capacity (GBs)']
cache_items = ['SP Read Cache State', 'SP Write Cache State', 'Dirty Cache Pages (MB)', 'SPA Read Cache State',
               'SPA Write Cache State', 'SPB Read Cache State', 'SPB Write Cache State']
agent_items = ['Agent Rev', 'Model', 'Model Type', 'Serial No']
spbusy_items = ['Prct Busy', 'Prct Idle']
power_temp_items = ['Name', 'Power Status', 'Power Present', 'Power Rolling Average', 'Temp Status', 'Temp Present',
                    'Temp Rolling Average']
disk_items = ['Enclosure', 'State']


def datagather():
    request_list = {
        'agent': 'getagent',
        'spbusy': 'getcontrol',
        'cache': 'cache -sp -info',
        'storagepool': 'storagepool -list -availableCap -consumedCap -subscribedCap -prcntFull -state -rtype -status',
        'luns': 'getlun',
        'faults': 'faults -list',
        'disks': 'getdisk -state',
        'env': 'environment -list -enclosure',
        'ports': 'getall -hba'
    }
    try:
        mkdir(TMP_DIR)
    except OSError:
        pass
    for request in request_list.keys():
        with popen(CONNECT + request_list[request]) as rawdata:
            with open(TMP_DIR   + request, 'w+') as textdata:
                textdata.write(rawdata.read())
    return 'OK'


def getinfo(path, items, value):
    with open(path, 'r') as parseit:
        data = []
        for line in parseit:
            for item in items:
                if item in line:
                    line = line.replace(" ", "")
                    line = line.rstrip()
                    data.append(line.split(':')[1])
                if len(data) == len(items):
                    print (data[items.index(value)])
                    data = []


def check_storagepool(items, name, value):
    jsonlist = []
    keys = ['{#NAME}']
    with open(TMP_DIR + 'storagepool', 'r') as parseit:
        data = []
        for line in parseit:
            for item in items:
                if item in line:
                    line = line.replace(" ", "")
                    line = line.rstrip()
                    data.append(line.split(':')[1])
            if len(data) == len(items):
                if value == 'discovery':
                    jsonlist.append(json.dumps(dict(zip(keys, data))))
                else:
                    if name in data:
                        print (data[items.index(value)])
                data = []
    if len(jsonlist):
        discovery(jsonlist)


def check_lun(items, name, value):
    jsonlist = []
    keys = ['{#NAME}']
    with open(TMP_DIR + 'luns', 'r') as rawdata:
        luns = []
        for line in rawdata:
            if "Name" in line and len(line.split()) < 3:
                luns.append(line.split()[1])
            for item in items:
                if item in line:
                    line = line.replace(" ", "")
                    line = line.rstrip()
                    luns.append(line.split(':')[1])
            if len(luns) == len(items) + 1:
                if value == 'discovery':
                    jsonlist.append(json.dumps(dict(zip(keys, luns))))
                else:
                    if name in luns:
                        print (luns[items.index(value) + 1])
                luns = []
    if len(jsonlist):
        discovery(jsonlist)


def check_faults():
    with open(TMP_DIR + 'faults', 'r') as parseit:
        print (parseit.readline())


def check_disk(items, name, value):
    jsonlist = []
    disks = []
    keys = ['{#NAME}']
    with open(TMP_DIR + "disks", 'r') as parseit:
        for line in parseit:
            if 'Enclosure' in line:
                line = line.rstrip()
                disks.append(line)
            if 'State' in line:
                line = line.rstrip()
                line = line.replace(" ", "")
                disks.append((line.split(':')[1]))
            if len(disks) == 2:
                if value == 'discovery':
                    jsonlist.append(json.dumps(dict(zip(keys, disks))))
                else:
                    if name in disks:
                        print (disks[items.index(value)])
                disks = []
    if len(jsonlist):
        discovery(jsonlist)


def check_power_temp(items, name, value):
    jsonlist = []
    data = []
    keys = ['{#NAME}']
    with open(TMP_DIR + 'env', 'r') as parseit:
        for line in parseit:
            if 'Bus' in line:
                line = line.rstrip()
                data.append(line)
            if 'Status' in line:
                line = line.rstrip()
                line = line.replace(" ", "")
                data.append((line.split(':')[1]))
            if 'Present' in line:
                line = line.rstrip()
                line = line.replace(" ", "")
                data.append((line.split(':')[1]))
            if 'Rolling' in line:
                line = line.rstrip()
                line = line.replace(" ", "")
                data.append((line.split(':')[1]))
            if len(data) == len(items):
                if value == 'discovery':
                    jsonlist.append(json.dumps(dict(zip(keys, data))))
                else:
                    if name in data:
                        print (data[items.index(value)])
                data = []
    if len(jsonlist):
        discovery(jsonlist)


def check_portstate(items, name, value):
    data = []
    keys = ['{#NAME}']
    spport = 0
    jsonlist = []
    with open(TMP_DIR + 'ports', 'r') as parseit:
        for line in parseit:
            if 'SPPORT' in line:
                spport = 1
            for item in items:
                if item in line:
                    line = line.replace(" ", "")
                    line = line.rstrip()
                    if spport:
                        data.append(line.split(':')[1])
                if len(data) == len(items):
                    spname = " ".join(data[0:2])
                    data.pop(0)
                    data.pop(0)
                    data.insert(0, spname)
                    if value == 'discovery':
                        jsonlist.append(json.dumps(dict(zip(keys, data))))
                    else:
                        if name in data:
                            print (data[items.index(value) - 1])
                    data = []
    if len(jsonlist):
        discovery(jsonlist)


def discovery(jsonlist):
    #dirty hax r dirty
    print ('{"data":')
    print (str(jsonlist).replace("'", ""))
    print ('}')


if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option("--gather", action="store_true")
    parser.add_option("--agent", action="store_true")
    parser.add_option("--cache", action="store_true")
    parser.add_option("--storagepool", action="store_true")
    parser.add_option("--spbusy", action="store_true")
    parser.add_option("--faults", action="store_true")
    parser.add_option("--powertemp", action="store_true")
    parser.add_option("--lun", action="store_true")
    parser.add_option("--disk", action="store_true")
    parser.add_option("--ports", action="store_true")
    parser.add_option('--name', action='store')
    parser.add_option('--item', action='store')
    parser.add_option('--ip', action='store')
    parser.add_option('--username', action='store')
    parser.add_option('--password', action='store')

    args, option = parser.parse_args()
#    try:
    if args.gather:
            print (datagather())
    if args.agent:
            getinfo(TMP_DIR + 'agent', agent_items, args.item)
    if args.cache:
            getinfo(TMP_DIR + 'cache', cache_items, args.item)
    if args.spbusy:
            getinfo(TMP_DIR + 'spbusy', spbusy_items, args.item)
    if args.storagepool:
            check_storagepool(storagepool_items, args.name, args.item)
    if args.lun:
            check_lun(lun_items, args.name, args.item)
    if args.ports:
            check_portstate(portstate_items, args.name, args.item)
    if args.faults:
            check_faults()
    if args.powertemp:
            check_power_temp(power_temp_items, args.name, args.item)
    if args.disk:
            check_disk(disk_items, args.name, args.item)
#    except :

