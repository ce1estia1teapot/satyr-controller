import aioble
import bluetooth
import sys

sys.path.append("")

from micropython import const

import uasyncio as asyncio

import random
import struct

# ====== 1. Initialize Bluetooth Services, Characteristics, and Settings ======
_ENV_SENSE_SERV_UUID = bluetooth.UUID(0x181A)
_ENV_SENSE_TEMP_UUID = bluetooth.UUID(0x2A6E)
_GENERIC_LEVEL_CHAR_UUID = bluetooth.UUID(0x2AF9)


# ====== 2. Define Helper Functions ======
async def scan_for_sensors():
    print('Initiating scan for satyr devices with data...')

    found_devices = []

    # Duration (ms), interval (us), window (us), and active (bool)
    async with aioble.scan(5000, 30000, 30000, active=True) as scanner:
        async for result in scanner:
            if ('satyr' in result.name()) and (_ENV_SENSE_SERV_UUID in result.services()):
                found_devices.append(result.device)

    return found_devices

async def validate_device(p_device):
    """
    A valid device is one we've either validated before and added to the list of valid devices, or one that is validated against
    the server.
    :return: A bool representing whether the provided device is a valid one
    """
    # TODO: Implement a record of previously connected devices and references to this list

    condition_1 = p_device is not None
    condition_2 = ('satyr' in p_device.name())

    total_condition = condition_1 and condition_2

    if total_condition:
        return True
    else:
        return False


async def get_readings_from_connection(p_connection):

    try:
        temp_service = await p_connection.service(_ENV_SENSE_SERV_UUID)
        temp_characteristic = await temp_service.characteristic(_GENERIC_LEVEL_CHAR_UUID)

    except asyncio.TimeoutError:
        print("Timeout discovering services/characteristics")
        return

    except AttributeError as e:
        print(f'AttributeError discovering services/characteristics: {e}')