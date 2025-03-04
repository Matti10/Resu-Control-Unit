
import socket
import network
def init_AP():
    SSID = "RCU_Prototype1"  # Name of your Wi-Fi network
    PASSWORD = "1234567890"         # Password (at least 8 characters)

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

import server
import RCU
import shiftLights
from machine import Timer
from machine import Pin
import time


config = RCU.import_config()


white = {'green': 255, 'blue': 255, 'red': 255}
# shift = shiftLights.ShiftLight(config)
rpm = 0
rpmTestTimer = Timer(0)
i = 0

def enable_test_rpm():
    rpmTestTimer.init(period=50, mode=Timer.PERIODIC, callback=lambda t: shift.set_color_fromRPM(rpm))
    
def enable_test_limiter():
    rpmTestTimer.init(period=150, mode=Timer.PERIODIC, callback=lambda t: shift.increment_limiter(config["ShiftLights"]["LimiterPattern"]["selected"],i))

    
def disable_test():
    rpmTestTimer.deinit()

def test_rpm():
    enable_test_rpm()
    global rpm
    for i in range(0, 8000):
        shift.update()
        rpm = rpm + 100
        time.sleep_ms(100)
        
    rpm = 0
    shift.clear_all()
    shift.update()
    disable_test()

def test_limiters():
    enable_test_limiter()
    
    for pattern in config["ShiftLights"]["LimiterPattern"]["Patterns"]:
        shift.set_limiter_pattern(pattern)
        time.sleep_ms(150*17)
        shift.clear_all()
            
    shift.update()
    disable_test()


serve = server.RCU_server(config)

# testIRQ = Pin(8, Pin.IN, Pin.PULL_UP)
# testIRQ.irq(trigger=Pin.IRQ_FALLING, handler=lambda t: print("IRQ")) 
