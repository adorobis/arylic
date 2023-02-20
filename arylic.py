# -*- coding: utf-8 -*-

#import subprocess
import json
import logging
import logging.handlers #Needed for Syslog
import sys
import time
import configparser
import os
import requests



# Read configuration from ini file
config = configparser.ConfigParser()
config.read(os.path.dirname(os.path.abspath(__file__)) + '/config.ini')
print(os.path.dirname(os.path.abspath(__file__)) + '/config.ini')
# Service Configuration
refresh_interval = int(config['DEFAULT']['REFRESH_INTERVAL']) # Interval in seconds at which speedtest will be run
MQTTServer = config['MQTT']['MQTTServer']            # MQTT broker - IP
MQTTPort = int(config['MQTT']['MQTTPort'])           # MQTT broker - Port
MQTTKeepalive = int(config['MQTT']['MQTTKeepalive']) # MQTT broker - keepalive
MQTTUser = config['MQTT']['MQTTUser']                # MQTT broker - user - default: 0 (disabled/no authentication)
MQTTPassword = config['MQTT']['MQTTPassword']        # MQTT broker - password - default: 0 (disabled/no authentication)
HAEnableAutoDiscovery = config['HA']['HAEnableAutoDiscovery'] == 'True' # Home Assistant send auto discovery
SPEEDTEST_SERVERID = config['DEFAULT']['SPEEDTEST_SERVERID'] # Remote server for speedtest
SPEEDTEST_PATH = config['DEFAULT']['SPEEDTEST_PATH'] # path of the speedtest cli application
DEBUG = int(config['DEFAULT']['DEBUG']) #set to 1 to get debug information.
CONSOLE = int(config['DEFAULT']['CONSOLE']) #set to 1 to send output to stdout, 0 to local syslog
HAAutoDiscoveryDeviceName = config['HA']['HAAutoDiscoveryDeviceName']            # Home Assistant Device Name
HAAutoDiscoveryDeviceId = config['HA']['HAAutoDiscoveryDeviceId']     # Home Assistant Unique Id
HAAutoDiscoveryDeviceManufacturer = config['HA']['HAAutoDiscoveryDeviceManufacturer']
HAAutoDiscoveryDeviceModel = config['HA']['HAAutoDiscoveryDeviceModel']


# Setup Logger 
_LOGGER = logging.getLogger(__name__)
if CONSOLE:
    formatter = \
        logging.Formatter('%(message)s')
    handler1 = logging.StreamHandler(sys.stdout)
    handler1.setFormatter(formatter)
    handler1.setLevel(logging.NOTSET)
    _LOGGER.addHandler(handler1)
else:
    formatter2 = logging.Formatter('%(levelname)s %(asctime)s %(filename)s - %(message)s')
    LOGFILE = os.path.dirname(os.path.abspath(__file__)) + '/arylic.log'
    handler2 = logging.handlers.RotatingFileHandler(LOGFILE, maxBytes=(1048576*5), backupCount=7)
    handler2.setFormatter(formatter2)
    handler2.setLevel(logging.NOTSET)
    _LOGGER.addHandler(handler2)

if DEBUG:
  _LOGGER.setLevel(logging.DEBUG)
else:
  _LOGGER.setLevel(logging.INFO)

def run_monitor():
    #Main monitor routine
    try:

        api_url = "http://10.144.1.153:8000/arylicstatus.json"
        print(api_url)
        response = requests.get(api_url)
        json_object = response.json()
        print(json_object)
        print(json_object["status"])

        api_url = "http://10.144.1.57/cm?cmnd=status%201"
        print(api_url)
        response = requests.get(api_url)
        json_object = response.json()
        print(json_object)
        print(json_object["StatusPRM"]["Uptime"])

    except:
        _LOGGER.info('API request failed')
        _LOGGER.info('Exception information:')
        _LOGGER.info(response)
    else:
        time.sleep(0.1)
        _LOGGER.debug('Error occured: %s', response)

run_monitor()

# Main loop of the program
# while True:
#     try:
#         run_monitor()
#         time.sleep(refresh_interval)
#         pass
#     except KeyboardInterrupt:
#         _LOGGER.error('Rynning arylic stopped by keyboard')
#         break
