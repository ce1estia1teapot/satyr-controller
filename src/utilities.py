import time
import network
import ujson as json

from machine import Pin, Timer
from network import WLAN


class DeviceSettings:

    secrets_fp = ""
    settings_fp = ""

    device_name = ""
    advertising_interval_ms = ""
    cache_size_bytes = ""
    last_network_ssid = ""
    last_network_pass = ""

    def __init__(self, p_settings=None):
        if p_settings is None:
            p_settings = {'secrets_fp': "src/secrets.json", 'settings_fp': "src/device_settings.json", 'device_name': "Satyr", 'advertising_interval_ms': 250000,
                          'cache_size_bytes': 100000, 'last_network_ssid': "", 'last_network_pass': ""}

        for attr in p_settings:
            self.__setattr__(attr, p_settings[attr])

        self._update_config_file()

    @staticmethod
    def initialize_from_files(p_config_fp=None, p_secrets_fp=None):
        """
        This method should take a filepath and return a DeviceSettings
        object after initializing it from a file
        :param p_secrets_fp:
        :param p_config_fp:
        :return: A DeviceSettings object initialized with values contained in the provided files
        """

        if (p_config_fp is None) or (p_secrets_fp is None):
            return DeviceSettings()
        else:
            try:
                # Load settings
                with open("src/device_settings.json", 'r') as file:
                    settings = json.load(file)
                # Load secrets
                with open("src/secrets.json", 'r') as file:
                    secrets = json.load(file)

                settings.update(secrets)
                settings.update({'secrets_fp': p_config_fp, 'settings_fp': p_secrets_fp})
                return DeviceSettings(p_settings=settings)

            except ValueError:
                print(f'Failed to initialize with settings or secrets at provided paths:\n'
                      f'Settings FP: {p_config_fp}\n'
                      f'Secrets FP: {p_secrets_fp}')
                return DeviceSettings()
            except NotImplementedError as e:
                raise e

    def _update_config_file(self):
        # TODO: Implement _update_config_file for DeviceSettings
        data = self.__dict__
        with open(self.config_fp, 'w') as file:
            json.dump(data, file)

        raise NotImplementedError()


def do_startup_blink(p_pin):
    i = 0
    p_pin.value(0)
    while i < 3:
        i += 1
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
