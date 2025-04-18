import network

import encrypt
from static import *

"""These are efficeively just wrappers for the network.WLAN class that implements very basic, insecure, encryption"""

class rcuNetwork:
    def __init__(
        self,
        ssid,
        password,
        networkType
    ):
        self.net = network.WLAN(networkType)
        self.ssid = ssid
        # self.mac = self.get_mac() # TODO Test if this is needed. Depending on whether the AP actually needs to be activated 
        self.encKey = encrypt.get_aes_key_fromMac(self.net.config('mac'))
        if password != AP_DEFAULT_PASSWORD: #for firsttime setup, all othertimes it will at minumum be an encrypted version of AP_DEFAULT_PASSWORD
            self.password = encrypt.decrypt(password, self.encKey)
        else:
            self.password = password
        
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
    def build_fromDict(obj):
        return rcuAP(
            obj[KEY_PASSWORD],
            obj[KEY_SSID],
            obj[KEY_IP],
            obj[KEY_SUB_MASK],
            obj[KEY_GATEWAY],
            obj[KEY_DNS],
        )
        
    def __init__(
        self,
        password = None,
        ssid = None,
        ip = "1.1.1.1",
        sub = "255.255.255.0",
        gateway = "1.1.1.1",
        dns =  "1.1.1.1"
    ):
        self.ip = ip
        self.sub= sub
        self.gateway= gateway
        self.dns= dns
        
        #default value for SSID
        if None == ssid:
            # ssid = f"RCU-{self.mac}"
            ssid = "Resu Control Unit"
        if None == password:
            password = AP_DEFAULT_PASSWORD

        super().__init__(
            ssid,
            password,
            network.AP_IF
        )

    def start(self):
        print("start")
        # Create an Access Point
        self.net.config(essid=self.ssid, password=self.password)
        self.net.active(True)
        print("end")

        # Wait until the AP is active
        while not self.net.active():
            pass
        
        
        self.net.ifconfig((self.ip, self.sub, self.gateway, self.dns)) 
        

    def to_dict(self):
        return {
            KEY_AP : super().to_dict()
        }

class rcuWLAN(rcuNetwork):
    @staticmethod
    def build_fromDict(obj):
        return rcuWLAN(
            obj[KEY_PASSWORD],
            obj[KEY_SSID]
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