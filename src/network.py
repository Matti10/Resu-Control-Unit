from re import S

from itsdangerous import NoneAlgorithm
import network
import encrypt

IP = "1.1.1.1"
SUB_MASK = "255.255.255.255"
AP_SSID_KEY = "ssid"
AP_KEY = "key"
AP_DEFAULT_KEY = "1234567890"
WLAN_KEY = "wlanKey"
WLAN_SSID_KEY = "wlanSSID"

class netoworkCredentials:
    def __init__(
        self,
        ssid,
        encKey,
        key
    ):
        self.ssid = ssid
        self.key = encrypt.decrypt(key, self.encKey)
        
    def set_credentials(self,key=None,ssid=None):
        if None == key:
            key = self.key
            
        if None == ssid:
            ssid = self.ssid
            
        self.ssid = ssid
        self.key = key

class rcuAP(netoworkCredentials):
    @staticmethod
    def from_loadedJson(jsonLoadedObj):
        return RCUNetwork(
            jsonLoadedObj[AP_KEY],
            jsonLoadedObj[AP_SSID_KEY]
        )
        
    def __init__(
        self,
        key = None,
        ssid = None,
    ):
        self.ap = network.WLAN(network.AP_IF)
        self.mac = self.get_ap_mac()
        self.encKey = encrypt.get_aes_key_fromMac(self.mac)
        
        if None == ssid:
            self.ssid = f"RCU-{self.mac}"
        else:
            self.ssid = ssid
        
        self.wlanSSID = wlanSSID
        
        if None == key:
            key = AP_DEFAULT_KEY
        else:

        
        if None == wlanKey:
            self.wlanKey = wlanKey
        else:
            self.wlanKey = encrypt.decrypt(wlanKey, self.encKey)
            

        
        self.init_AP()
    
    def to_dict(self):
        return self.__dict__
    
    def get_ap_mac(self):
        apActive = self.ap.active() # store current ap state
        if not apActive:
            self.ap.active(True) #activate ap if its not on
        mac = self.ap.config('mac')
        
        self.ap.active(apActive) #restore previous state
        
        return mac
        
    
    def init_AP(self):
        # Create an Access Point
        self.ap.config(essid=self.ssid, password=self.key)
        self.ap.active(True)

        # Wait until the AP is active
        while not self.ap.active():
            pass
        
        self.ap.ifconfig((IP, SUB_MASK, IP, IP)) 
        
class rcuWLAN(netoworkCredentials):
    def __init__(
        self,
        key = None,
        ssid = None,
    ):
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan
        self.encKey = encrypt.get_aes_key_fromMac(self.mac)
        
        if None == ssid:
            self.ssid = f"RCU-{self.mac}"
        else:
            self.ssid = ssid
        
        self.wlanSSID = wlanSSID
        
        if None == key:
            key = AP_DEFAULT_KEY
        else:

        
        if None == wlanKey:
            self.wlanKey = wlanKey
        else:
            self.wlanKey = encrypt.decrypt(wlanKey, self.encKey)
            
    
    def from_loadedJson(jsonLoadedObj):
        return rcuWLAN(
            jsonLoadedObj[WLAN_KEY],
            jsonLoadedObj[WLAN_SSID_KEY],
        )