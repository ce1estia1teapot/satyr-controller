import sys

sys.path.append("")

import aioble
import uasyncio as asyncio
import bluetooth
import ujson as json
import mip
import network
import random
import struct
import time

from machine import Pin, Timer
from micropython import const
from src.utilities import do_startup_blink, network_scan_for_ssid, network_connect_by_ssid
from src.ble.file_client_ble_utilities import scan_for_sensors, validate_device

# ===== 1. Boot: Load secrets and attempt network connection =====
# Defining LED Pin and setting to off
led_pin = Pin("LED", Pin.OUT)
led_pin.off()

with open("src/secrets.json", 'r') as file:
    secrets = json.load(file)

# Defining Network
nic = network.WLAN(network.STA_IF)
nic.active(True)

is_connected_wifi: bool = network_connect_by_ssid(p_network=nic, p_ssid=secrets['network_ssid'],
                                                  p_pass=secrets['network_password'])

# 1a: If successful, continue to 2
if is_connected_wifi:
    pass

# 1b: If network connection unsuccessful, enter BLE pairing mode
else:
    print('Not connected to wifi')
    sys.exit()
    # 1bi: Advertise ble connection
    # 1bii: Connect to smart phone
    # 1biii: Prompt, requesting credentials
    # 1biv: Receive and parse credentials
    # 1bv: validate credentials by connecting to network
    # 1bvi: If successful, write secrets to file and continue to 2. Else, repeat 1b


# ===== 2. Main Loop =====
async def main():
    while True:
        # 2a: Scan for connections
        found_devices = await scan_for_sensors()
        # 2ai: If there are interesting devices, validate
        valid_devices = [x for x in found_devices if validate_device(x)]
        # 2aii: Receive files from each validated device
        # 2b: Attempt to uplink cached measurements to server

# ===== 3. Check with server whether there are any code/settings updates for sensors

# ===== Final: Run main and update methods