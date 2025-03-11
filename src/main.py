import socket
import network
import server
import RCU
import shiftLights
import asyncio
from machine import Timer
from machine import Pin
import time
import testing_utils
import rpmReader

def init_AP():
    SSID = "RCU_Prototype1"  # Name of your Wi-Fi network
    PASSWORD = "1234567890"  # Password (at least 8 characters)

    # Create an Access Point
    ap = network.WLAN(network.AP_IF)
    ap.config(essid=SSID, password=PASSWORD)
    ap.active(True)

    # Wait until the AP is active
    while not ap.active():
        pass
    
    ap.ifconfig(("1.1.1.1", "255.255.255.0", "1.1.1.1", "1.1.1.1")) 

    print("Access Point Active!")
    print("IP Address:", ap.ifconfig()[0])

init_AP()

config = RCU.import_config()

white = {'green': 255, 'blue': 255, 'red': 255}
shift = shiftLights.ShiftLight(config)

tachoGen = testing_utils.GenerateTachoSignal(Timer(0), config["RPMReader"]["tachoMode"]["pulsesPerRevolution"], rpm=5)
tachoRead = rpmReader.RPMReader(config, Timer(1))
tachoRead.start_tacho()

async def test():
    i = 0
    while True:
        i += 1
        if i > 5:
            tachoGen.set_rpm(tachoGen.rpm + 501)
            i = 0
        elif tachoGen.rpm > 18000:
            break
        rpm = tachoRead.get_rpm()
        print(f"main loop rpm {rpm}")
        await asyncio.sleep(0.05)

async def main():
    shiftTask = asyncio.create_task(shift.run(tachoRead.get_rpm))
    await test()
    await shiftTask

asyncio.run(main())
