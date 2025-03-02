

import network
def init_AP():
    SSID = "ESP32-Access-Point"  # Name of your Wi-Fi network
    PASSWORD = "12345678"         # Password (at least 8 characters)

    # Create an Access Point
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid=SSID, password=PASSWORD)

    # Wait until the AP is active
    while not ap.active():
        pass

    print("Access Point Active!")
    print("IP Address:", ap.ifconfig()[0])



