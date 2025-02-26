# import neopixel
# from RCU_Function import RCU_Function

PIN_FUNCNAME_SHIFTLIGHTS = "ShiftLights"
PIN_UNASSIGN_NAME = "Unassigned"

class ShiftLight:
    def __init__(self,config):
        self.config = config
        self.lightCount = len(self.config["ShiftLights"]["ShiftLights"])
        self.rpmStep = (self.config["ShiftLights"]["endRPM"] - self.config["ShiftLights"]["startRPM"])/self.lightCount
        if len(self.config["ShiftLights"]["pinIDs"]) > 0:
            self.outputPinID = self.config["ShiftLights"]["pinIDs"][0]
        else:
            self.outputPinID = None
        # super().__init__(config["pinIDs"], "ShiftLights", config)

        # self.np = neopixel.NeoPixel(self.pins[0],self.lightCount)
        self.np = []
        
    def setAll_color(self,color):
        for i in range(self.lightCount):
            self.set_color(i,color)
            
    def clear_all(self):
        self.setAll_color({"red":0,"green":0,"blue":0})
            
    def set_color(self, id, color):
        self.np[id] = (color["red"],color["blue"],color["green"])
        
    # def set_limiter(self):
    #     self.setAll_color(self.config["ShiftLights"]["LimiterColor"]["color"])
        
    def increment_limiter(self, limiterType = None, i=0):
        if None == limiterType or limiterType not in self.config["ShiftLights"]["ShiftLights"]["LimiterPattern"]["patterns"]:
            limiterType = self.config["ShiftLights"]["ShiftLights"]["LimiterPattern"]["selected"]

        
        if limiterType == "Wave Left": #left to right
            self.set_color(i,self.config["ShiftLights"]["LimiterColor"]["color"])
        elif limiterType == "Wave Right": #right to left
            self.set_color(self.lightCount - i,self.config["ShiftLights"]["LimiterColor"]["color"])
        elif limiterType == "Wave Center Out": #center out
            mid = self.lightCount // 2 + (self.lightCount % 2)
            
            self.set_color(mid+i,self.config["ShiftLights"]["LimiterColor"]["color"])
            self.set_color(mid-i,self.config["ShiftLights"]["LimiterColor"]["color"])
        elif limiterType == "Wave Center In": #center in
            self.set_color(i,self.config["ShiftLights"]["LimiterColor"]["color"])
            self.set_color(self.lightCount-i,self.config["ShiftLights"]["LimiterColor"]["color"])
            self.setAll_color(self.config["ShiftLights"]["LimiterColor"]["color"])
        elif limiterType == "Flash":
            if i % 2 == 0:
                self.setAll_color(self.config["ShiftLights"]["LimiterColor"]["color"])
            else:
                self.clear_all()
        else:#  limiterType == "Solid"
                self.setAll_color(self.config["ShiftLights"]["LimiterColor"]["color"])

        i += 1
        return i
    
    def handle_limiter(self):
        # start timer, timing depends on limiter pattern
        i = self.increment_limiter
    
    def set_color_fromRPM(self,rpm):
        if rpm >= self.config["ShiftLights"]["endRPM"]:
            self.handle_limiter()
        else:
            for i in range(self.lightCount):
                # if the rpm is greater or equal the the RPM needed to turn on light
                if rpm >= (self.config["ShiftLights"]["startRPM"] + i * self.rpmStep):
                    #set light to color in config["ShiftLights"]
                    self.np[i] = (
                        self.config["ShiftLights"]["ShiftLights"][i]["red"],
                        self.config["ShiftLights"]["ShiftLights"][i]["blue"],
                        self.config["ShiftLights"]["ShiftLights"][i]["green"]
                    )
                else: 
                    #set light to be off
                    self.np[i] = (0,0,0)
        
    def set_limiter_pattern(self,pattern):
        self.config["ShiftLights"]["LimiterPattern"]["Selected"] = pattern
        print(f"Set limiter pattern to: {self.config["ShiftLights"]["LimiterPattern"]["Selected"]}")
        
    def set_light_config_color(self,lightsConfig,color):
        red,green,blue = color
        
        lightsConfig["color"]["red"] = red
        lightsConfig["color"]["green"] = green
        lightsConfig["color"]["blue"] = blue
    
    def set_configed_color(self, id, color):
        self.set_light_config_color(self.config["ShiftLights"]["ShiftLights"][id],color)
        print(self.config["ShiftLights"]["ShiftLights"][id])
        
    def set_configed_limiter_color(self,color):
        self.set_light_config_color(self.config["ShiftLights"]["LimiterColor"],color)
        print(self.config["ShiftLights"]["LimiterColor"])
        
    def get_shiftLights(self):
        return self.config["ShiftLights"]
    
    def set_pin(self,pinID):
        if pinID == PIN_UNASSIGN_NAME:
            self.unassign_pin()
            return
        
        # Clear old Pin
        if self.config["ShiftLights"]["pinIDs"] != []:
            self.config["Pins"]["Pins"][self.config["ShiftLights"]["pinIDs"][0]]["function"] = ""
        
        # Set new pin
        self.config["ShiftLights"]["pinIDs"] = [pinID]
        self.config["Pins"]["Pins"][pinID]["function"] = PIN_FUNCNAME_SHIFTLIGHTS
        self.outputPinID = pinID
        print(f"Set pin to {pinID}")
        
    def unassign_pin(self):
        if self.outputPinID != None:
            self.config["ShiftLights"]["pinIDs"] = []
            print(self.outputPinID)
            print(type(self.outputPinID))
            self.config["Pins"]["Pins"][self.outputPinID]["function"] = ""
            self.outputPinID = None