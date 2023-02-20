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
DEBUG = int(config['DEFAULT']['DEBUG']) #set to 1 to get debug information.
CONSOLE = int(config['DEFAULT']['CONSOLE']) #set to 1 to send output to stdout, 0 to local syslog
TESTING_MODE = int(config['DEFAULT']['TESTING_MODE'])
ArylicIP = config['DEFAULT']['ARYLIC_IP']
PlugIP = config['DEFAULT']['PLUG_IP']


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
    if TESTING_MODE:
        arylic_url = "http://"+ArylicIP
        print(arylic_url)
    else:
        arylic_url = "http://"+ArylicIP+"/httpapi.asp?command=getPlayerStatus"
        print(arylic_url)
    try:
        response = requests.get(arylic_url)
        json_object = response.json()
        print(json_object)
        print(json_object["status"])
        status = json_object["status"]
        title = json_object["Title"]
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
        _LOGGER.info(f"Unexpected {err=}, {type(err)=}")
        plug_uptime = check_plug()
        if plug_uptime > 180:
            restart_switch()
        
    
    if status != "play":
        preset = str(read_preset())
        if TESTING_MODE:
            preset_url = "http://"+ArylicIP+"/httpapi.asp?command=MCUKeyShortClick:"+preset
            print(preset_url)
            preset_url = arylic_url
        else:
            preset_url = "http://"+ArylicIP+"/httpapi.asp?command=MCUKeyShortClick:"+preset
            print(preset_url)
        try:
            response = requests.get(preset_url)
            json_object = response.json()
            print(json_object)
        except Exception as err:
            print(f"Unexpected {err=}, {type(err)=}")
            _LOGGER.info(f"Unexpected {err=}, {type(err)=}")
    else:
        if title == "526164696F204E6F7779205377696174" or title == "556E6B6E6F776E" or title == "": 
            store_preset(1)
        if title == "526164696F20333537": 
            store_preset(2)
        if title == "526164696F2042616F626162": 
            store_preset(3)
        if title == "526F636B536572776973464D": 
            store_preset(4)
        


def check_plug():
    plug_url = "http://"+PlugIP+"/cm?cmnd=status%201"
    print(plug_url)
    try:
        response = requests.get(plug_url)
        json_object = response.json()
        print(json_object)
        print('Uptime raw:', json_object["StatusPRM"]["Uptime"])
        h,m,s = json_object["StatusPRM"]["Uptime"][2:10].split(':')
        uptime_sec = int(h)*3600 + int(m)*60 + int(s)
        print('Uptime:', json_object["StatusPRM"]["Uptime"][2:10])
        print('Uptime seconds:', uptime_sec)
        return int(uptime_sec)
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
        _LOGGER.info(f"Unexpected {err=}, {type(err)=}")

def restart_switch():
    
    plug_off_url = "http://"+PlugIP+"/cm?cmnd=Power%20OFF"
    plug_on_url = "http://"+PlugIP+"/cm?cmnd=Power%20ON"
    try:
        response = requests.get(plug_off_url)
        json_object = response.json()
        print(json_object)
        time.sleep(2)
        response = requests.get(plug_on_url)
        json_object = response.json()
        print(json_object)
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
        _LOGGER.info(f"Unexpected {err=}, {type(err)=}")

def read_preset():
    # JSON file
    f = open ('status.json', "r")
    
    # Reading from file
    data = json.loads(f.read())
    
    # Closing file
    f.close()
    return data['preset']

def store_preset(preset = 1):
    dict1 ={ 
        "preset": preset, 
    } 
   
    # the json file where the output must be stored 
    out_file = open("status.json", "w") 
    
    json.dump(dict1, out_file, indent = 6) 
    
    out_file.close()




# Main loop of the program
while True:
    try:
        run_monitor()
        time.sleep(refresh_interval)
        pass
    except KeyboardInterrupt:
        _LOGGER.error('Rynning arylic stopped by keyboard')
        break
