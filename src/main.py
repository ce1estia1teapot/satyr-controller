import sys

import machine

sys.path.append("")

import aioble
import uasyncio as asyncio
import urequests
import bluetooth
import ujson as json
import mip
import network
import random
import struct
import time

from machine import Pin, Timer
from micropython import const
from src.utilities import DeviceSettings, do_startup_blink, network_scan_for_ssid, network_connect_by_ssid
from src.ble.string_ble_utils import scan_for_sensors, validate_device

# #TODO: Enable specifying default settings for new sensors which they pull from the server on first boot

# ===== 1. Boot and Initialize: Load secrets and attempt network connection =====
# Defining LED Pin and setting to off
led_pin = Pin("LED", Pin.OUT)
led_pin.off()
do_startup_blink(led_pin)

# Loading device settings
device_settings = DeviceSettings.initialize_from_files(p_config_fp='src/device_settings.json', p_secrets_fp='src/secrets.json')

m_connected_devices = []
m_connections = []

# Defining Network
nic = network.WLAN(network.STA_IF)
nic.active(True)

is_connected_wifi: bool = network_connect_by_ssid(p_network=nic, p_ssid=device_settings.last_network_ssid,
                                                  p_pass=device_settings.last_network_pass)

# 1a: If successful, continue to 2
if is_connected_wifi:
    pass

# 1b: If network connection unsuccessful, enter BLE pairing mode
else:
    print('Not connected to wifi')
    pass
    # TODO: Implement connection retry protocol in main.py
    # 1bi: Advertise ble connection
    # 1bii: Connect to smart phone
    # 1biii: Prompt, requesting credentials
    # 1biv: Receive and parse credentials
    # 1bv: validate credentials by connecting to network
    # 1bvi: If successful, write secrets to file and continue to 2. Else, repeat 1b


# ===== 2. Main Loop =====
async def main():
    global device_settings

    while True:
        # 2a: Scan for connections
        found_devices = await scan_for_sensors()

        # 2ai: If there are interesting devices, validate and add to archive of devices
        for device in found_devices:
            if validate_device(device) and (device not in m_connected_devices):
                m_connected_devices.append(device)

        # 2aii: Try connecting to all previously connected devices
        if len(m_connected_devices) > 0:
            print(f'Contacting and polling {len(m_connected_devices)} devices...')
            for device in m_connected_devices:
                # Establish connection
                print(f'Connecting to {device}')
                try:
                    print("Connecting to", device)
                    connection = await device.connect()
                    m_connections.append(connection)
                except asyncio.TimeoutError:
                    print("Timeout during connection")
                    return
                except AttributeError as e:
                    print(f'AttributeError discovering services/characteristics: {e}')

            # Wait for writes to subscribed characteristic(s) for all active connections
            if len(m_connections) > 0:
                raise NotImplementedError()

        else:
            print(f'No devices in archive to connect with')

        time.sleep(device_settings.controller_poll_interval_ms / 1000)

        # 2b: Attempt to uplink cached measurements to server
        # TODO: Implement server uplink and local records flush on controller

# ===== 3. Check with server whether there are any code/settings updates for sensors
# TODO: Implement 'watchtower' function to handle settings changes for controller, sensors

# ===== Final: Run main and update methods
asyncio.run(main())