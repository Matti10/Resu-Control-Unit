import network
import time

# Connect to Wi-Fi
def connect_to_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)  # Set the ESP32 to station mode
    wlan.active(True)  # Activate the Wi-Fi interface
    flag = True
    while (flag):
        try:
            wlan.connect(ssid, password)  # Connect to the specified network
            flag = False
        except Exception as e:
            print(e)
            time.sleep(1)
            print("retrying")
            
            

    print("Connecting to Wi-Fi...")
    # Wait for connection
    while not wlan.isconnected():
        print(".", end="")
        time.sleep(1)

    print("\nConnected!")
    print("Network Config:", wlan.ifconfig())  # Print the network configuration

# Call the function
connect_to_wifi("Telstra19DB6D", "6qn28x5dm7")