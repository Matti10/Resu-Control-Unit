import network

import encrypt
from static import *

"""These are efficeively just wrappers for the network.WLAN class that implements very basic, insecure, encryption"""

class rcuNetwork(network.WLAN):
    def __init__(
        self,
        ssid,
        type,
        password
    ):
        self.net = super().__init__(type)
        self.net.active(True)
        self.ssid = ssid
        # self.mac = self.get_mac() # TODO Test if this is needed. Depending on whether the AP actually needs to be activated 
        self.encKey = encrypt.get_aes_key_fromMac(self.net.config('mac'))
        if password != AP_DEFAULT_PASSWORD: #for firsttime setup, all othertimes it will at minumum be an encrypted version of AP_DEFAULT_PASSWORD
            self.password = encrypt.decrypt(password, self.encKey)
        
    def set_credentials(self,password=None,ssid=None):
        if None == password:
            password = self.password
            
        if None == ssid:
            ssid = self.ssid
            
        self.ssid = ssid
        self.password = password

    def get_mac(self): #TODO depending on if the AP needs activating (i.e. current implementation works) this can be deleted
        apActive = self.net.active() # store current ap state
        if not apActive:
            self.net.active(True) #activate ap if its not on
        mac = self.net.config('mac')
        
        self.net.active(apActive) #restore previous state
        
        return mac
    
    def to_dict(self):
        return {
            KEY_SSID : self.ssid,
            KEY_PASSWORD : encrypt.encrypt(self.password,self.encKey)
        }



class rcuAP(rcuNetwork):
    @staticmethod
    def from_loadedJson(jsonLoadedObj):
        return rcuAP(
            jsonLoadedObj[KEY_PASSWORD],
            jsonLoadedObj[KEY_SSID]
        )
        
    def __init__(
        self,
        password = AP_DEFAULT_PASSWORD,
        ssid = None,
    ):
        #default value for SSID
        if None == ssid:
            ssid = f"RCU-{self.mac}"
        
        super().__init__(
            ssid,
            password,
            network.AP_IF
        )

    def start(self):
        # Create an Access Point
        self.net.config(essid=self.ssid, password=self.password)
        self.net.active(True)

        # Wait until the AP is active
        while not self.net.active():
            pass
        
        self.net.ifconfig((IP, SUB_MASK, IP, IP)) 

    def to_dict(self):
        return {
            KEY_AP : super().to_dict()
        }

class rcuWLAN(rcuNetwork):
    @staticmethod
    def from_loadedJson(jsonLoadedObj):
        return rcuWLAN(
            jsonLoadedObj[KEY_PASSWORD],
            jsonLoadedObj[KEY_SSID]
        )
    
    def __init__(
        self,
        password = None,
        ssid = None,
    ):

        if None != password and None != ssid: #Its pretty likely that this wifi interface wont be used. as such, dont init it until its needed
            self.setup(password, ssid)

    def setup(self,password,ssid):
        super().__init__(
            ssid,
            password,
            network.STA_IF
        )

    def _connect(self):
        self.net.active(True)
        self.net.connect(self.ssid,self.password)