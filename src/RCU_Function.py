
class RCU_Function:
    def __init__(self,pinIDs,name,config):
        self.pins = []

        for pinID in pinIDs:
            self.set_pin(pinID,config["pinConfig"][pinID]["function"],config["Pins"]["Pins"])
        
        self.name = name
        
    def set_pin(self,pinID,pinFunction,pinConfig):
        pinConfig[pinID]["function"] = pinFunction
        self.pins.append(pinConfig[pinID])
