# import socket
# import network
# import server
# import RCU
# import shiftLights
# from machine import Timer
# from machine import Pin
# import time
# import testing_utils
# import rpmReader

# def init_AP():
#     SSID = "RCU_Prototype1"  # Name of your Wi-Fi network
#     PASSWORD = "1234567890"  # Password (at least 8 characters)

#     # Create an Access Point
#     ap = network.WLAN(network.AP_IF)
#     ap.config(essid=SSID, password=PASSWORD)
#     ap.active(True)

#     # Wait until the AP is active
#     while not ap.active():
#         pass
    
#     ap.ifconfig(("1.1.1.1", "255.255.255.0", "1.1.1.1", "1.1.1.1")) 

#     print("Access Point Active!")
#     print("IP Address:", ap.ifconfig()[0])

# init_AP()

# config = RCU.import_config()

# white = {'green': 255, 'blue': 255, 'red': 255}
# shift = shiftLights.ShiftLight(config)

# tachoGen = testing_utils.GenerateTachoSignal(Timer(0), config["RPMReader"]["tachoMode"]["pulsesPerRevolution"], rpm=5)
# tachoRead = rpmReader.RPMReader(config, Timer(1))
# tachoRead.start_tacho()

# async def test():
#     i = 0
#     rpmToAdd = 500
#     while True:
#         if tachoGen.rpm > 12000:
#             rpmToAdd = -1000

#         tachoGen.set_rpm(tachoGen.rpm + rpmToAdd)
#         rpm = tachoRead.get_rpm()
#         print(f"main loop rpm {rpm}")
#         if ((rpm + rpmToAdd) <= 100):
#             break
#         await asyncio.sleep(0.3)

# async def main():
#     shiftTask = asyncio.create_task(shift.run(tachoRead.get_rpm))
#     await test()
#     await shiftTask


# asyncio.run(main())


import uasyncio as asyncio
import CAN
from machine import Pin
import time

# PIN_CAN_TX = 19
# PIN_CAN_RX = 22
PIN_CAN_TX = 22
PIN_CAN_RX = 19
PIN_CAN_MODE = 21

CAN_MODE_HIGH_SPEED = 0

canMode = Pin(PIN_CAN_MODE, Pin.OUT)
canMode.value(CAN_MODE_HIGH_SPEED)

def send_and_check(can_bus, name, id, expected_result=True, extended=False):
    can_bus.clear_tx_queue()
    can_bus.clear_rx_queue()
    can_bus.send([], id, extframe=extended)
    time.sleep_ms(100)
    if can_bus.any() == expected_result:
        print("{}: OK".format(name))
        if expected_result:
            can_bus.recv()
    else:
        print("{}: FAILED".format(name))

# dev = CAN(0, extframe=False, tx=PIN_CAN_TX, rx=PIN_CAN_RX, mode=CAN.NORMAL, baudrate=500000, auto_restart=False)

# send_and_check(dev,"RPM Test",0x010C)

test1 = Pin(39,mode=Pin.IN,pull=Pin.PULL_DOWN)
# test1.irq(lambda p:print("pin39"),trigger=Pin.IRQ_RISING)
test2 = Pin(33,mode=Pin.IN,pull=Pin.PULL_DOWN)
# test2.irq(lambda p:print("pin33"),trigger=Pin.IRQ_RISING)