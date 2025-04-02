# import RCU
# from static import *
# import asyncio

# rcu = RCU.RCU()

# sl = rcu.add_RCUFunc(SHIFTLIGHT_TYPE)
# sl = rcu.add_RCUFunc(RPMREADER_TYPE)
# asyncio.run(rcu.init_all_RCUFuncs())

# rcu.export_config(configPath="/workspaces/Resu-Control-Unit/src/data/test-config.json")

import uasyncio as asyncio
import CAN
import time
from machine import Pin

pwr = Pin(21,Pin.OUT)
pwr.value(0)
dev = CAN(0, extframe=False, tx=19, rx=22, mode=CAN.LOOPBACK, baudrate=500000, auto_restart=False)
# dev.send([0,0,0,0,0,0,0,0], 0x305)
# dev.restart()

# - identifier of can packet (int)
# - extended packet (bool)
# - rtr packet (bool)
# - data frame (0..8 bytes)

def run():
    i = 0
    while True:
        log("-")
        if dev.any():
            data = dev.recv()
            # log(f"id:{hex(data[0])}, ex:{data[1]}, rtr:{data[2]}, data:{data[3]}")
            log("e")
        # await asyncio.sleep(0.01)
        time.sleep(0.4)

        i += 1
        if i == 10:
            log("send ACK")
            dev.send([0,0,0,0,0,0,0,0], 0x305)
            i = 0

        
def log(str):
    with open("log.txt", "w") as f:
        f.write(f"{str}\n")
        
def print_log():
    # Open the file in read mode ('r')
    with open("log.txt", "r") as file:
        # Read the entire content of the file
        content = file.read()

    # Print the content
    print(content)