# Zabbix template for EMC_VNX_Monitoring
This project is a pyhton script and a zabbix template for monitor EMC VNX series. Product by Iman Mir <iman.mir@gmail.com>
Under GNU GPL licence
## Features
* Realtime monitor without any additional license
* montior overall status 
* monitor cache status
* monitor power usage and health status
* monitor disk status (remove or failed)
* montior luns usage and health
* monitor hardware I/O ports
* monitor SP status , temperature , ....

## Building
Install naviseccli and update emc_clarrion.py Line 13 NAVICLI={naviseccli path}
Clone project and copy  emc_clariion.py to  /usr/lib/zabbix/externalscripts/ and import template file

## Macro parameter
* {$EMCPASS}  Password of VNX storage
* {$EMCUSER}  Username of VNX storage

and enjoy

   
   
