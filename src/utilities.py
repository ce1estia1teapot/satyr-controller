import time
import network
import ujson as json

from machine import Pin, Timer
from network import WLAN


class DeviceSettings:
    config_fp = ""

    device_name = ""
    advertising_interval_ms = ""
    cache_size_bytes = ""
    last_network_ssid = ""
    last_network_pass = ""

    def __init__(self, p_config_fp = None):
        if p_config_fp is not None:
            self.config_fp = p_config_fp
            self._initialize_from_file(p_fp=p_config_fp)
        else:
            self._initialize_with_defaults()

    def _initialize_from_file(self, p_fp=None):
        if p_fp is None:
            return None

    def _initialize_with_defaults(self):

        device_name = "Satyr"
        advertising_interval_ms = 250000
        cache_size_bytes = 100000

    def _update_config_file(self):
        data = {k: v for k, v in self.__dict__}
        with open(self.config_fp, 'w') as file:
            json.dump(data, file)


def do_startup_blink(p_pin):
    i=0
    p_pin.value(0)
    while i<3:
        i+=1
        p_pin.value(1)
        time.sleep(0.2)
        p_pin.value(0)
        time.sleep(0.2)

def network_scan_for_ssid(p_network=None, p_ssid=None):
    """
    Scans for available networks whose SSID match the provided SSID
    
    p_network: a WLAN object from Network library. Used for scanning
    p_ssid: str SSID of the desired network
    
    returns: A network object representing whether the provided SSID represents a valid network
    """
    
    # Scanning for WiFi networks
    scan_results = p_network.scan()
    for net in scan_results:
        print(f'SSID: {net[0]}')

    # Searching scan results for my network
    good_network = None
    for temp_net in scan_results:
        ssid, bssid, channel, RSSI, security, hidden = temp_net
        if 'cheese' in str(ssid):
            good_network = temp_net
            print(f'Network found: {str(good_network[0])}')
    if good_network is None:
        print('Network not found')
        exit
    else:
        return good_network
    

def network_connect_by_ssid(p_network=None, p_ssid=None, p_pass=None, p_numAttempts=10):
    """
    p_network: a WLAN object from Network library
    p_ssid: A str representing the SSID of the desired network
    p_numAttempts: An int number of times to attempt connection before reporting failure
    
    returns: A bool representing whether the connection was successfully established
    """
    if p_network is None:
        return None
    if p_ssid is None:
        return None
    if p_pass is None:
        return None
    
    # Attempting Connection...
    print(f'Connecting to: {p_ssid}...')
    p_network.connect(ssid=p_ssid, key=p_pass)
    while not p_network.isconnected():
        print('...')
        time.sleep(1.0)
    if p_network.isconnected():
        print(f'Successfully connected')
        print(f'Network information: {p_network.ifconfig()}')
        return True
    else:
        return False
