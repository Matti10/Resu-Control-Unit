import time


PIN_FUNCNAME_SHIFTLIGHTS = "ShiftLights"
PIN_UNASSIGN_NAME = "Unassigned"



class ShiftLight:
    def __init__(self,config,testMode=False):
        self.config = config
        self.lightCount = len(self.config["ShiftLights"]["ShiftLights"])
        self.rpmStep = (self.config["ShiftLights"]["endRPM"] - self.config["ShiftLights"]["startRPM"])/self.lightCount
        self.testMode = testMode
        self.lightMidPoint =  self.lightCount // 2 + (self.lightCount % 2) - 1 # magic number 1 is to account for 0 index

        if not self.testMode:
            import neopixel
            self.neopixel = neopixel

            from machine import Pin
            self.Pin = Pin

        if len(self.config["ShiftLights"]["pinIDs"]) > 0:
            self.outputPinID = self.config["ShiftLights"]["pinIDs"][0]
            self.init_np()
        else:
            self.outputPinID = None
            self.np = None

    def init_np(self):
        if self.testMode:
            self.np = [0 for i in range(self.lightCount)]
        else:
            self.np = self.neopixel.NeoPixel(self.Pin(self.config["Pins"]["Pins"][self.outputPinID]["FirmwareID"], self.Pin.OUT),self.lightCount)
        
    def setAll_color(self,color):
        for i in range(self.lightCount):
            self.set_color(i,color)
            
    def clear_all(self):
        self.setAll_color({"red":0,"green":0,"blue":0})
            
    def set_color(self, id, color):
        # color adjustments now done on client side. 
        self.np[id] = (color["red"],color["green"],color["blue"])
    
    def increment_limiter(self, limiterType = None, i=0):
        #TODO refactor so comparisons aren't permormed every time
        if limiterType == None:
            limiterType = self.config["ShiftLights"]["LimiterPattern"]["selected"]
        print(limiterType)
        if i == 0:
            print("clearing all")
            self.clear_all()
        
        if limiterType == "Left to Right": #left to right
            print("waving left")
            self.set_color(i,self.config["ShiftLights"]["LimiterColor"][i]["color"])
        elif limiterType == "Right to Left": #right to left
            self.set_color(self.lightCount-(i+1),self.config["ShiftLights"]["LimiterColor"][self.lightCount-(i+1)]["color"])
        elif limiterType == "Center Out": #center out
           
            self.set_color(self.lightMidPoint+i,self.config["ShiftLights"]["LimiterColor"][self.lightMidPoint+i]["color"])
            self.set_color(self.lightMidPoint-i,self.config["ShiftLights"]["LimiterColor"][self.lightMidPoint-i]["color"])
            print(f"lightMidPoint-1:{self.lightMidPoint-1}")            
            print(f"lightMidPoint+i:{self.lightMidPoint+i}")
            print(f"lightMidPoint-i:{self.lightMidPoint-i}")
            if i >= self.lightMidPoint:
                i = 0
        elif limiterType == "Center In": #center in
            self.set_color(i,self.config["ShiftLights"]["LimiterColor"][i]["color"])
            self.set_color(self.lightCount-(i+1),self.config["ShiftLights"]["LimiterColor"][self.lightCount-(i+1)]["color"])

            if i >= self.lightMidPoint:
                i = 0
            # self.setAll_color(self.config["ShiftLights"]["LimiterColor"]["color"])
        elif limiterType == "Flash":
            if i % 2 == 0:
                self.setAll_color_fromConfig(subKey="LimiterColor")
            else:
                self.clear_all()
        else:# default limiterType == "Solid"
                self.setAll_color_fromConfig(subKey="LimiterColor")
            
        if i >= self.lightCount:
            i = 0
        else:
            i += 1
            
        return i
    
    def handle_limiter(self, limiterType = None):
        # start timer, timing depends on limiter pattern
        if None == limiterType or limiterType not in self.config["ShiftLights"]["LimiterPattern"]["patterns"]:
            limiterType = self.config["ShiftLights"]["LimiterPattern"]["selected"]
            print(f"Setting limiter to {limiterType} due to either no value being passed, or an invalid value being passed")
        
        i = self.increment_limiter
        
    def sample_limiter(self):
        counter = 0
        i = 0
        while counter < self.lightCount: 
            print(f"i:{i}")
            i = self.increment_limiter(self.config["ShiftLights"]["LimiterPattern"]["selected"],i)
            self.update()
            time.sleep_ms(25) #TODO make this an interupt so it doesn't lockup the loop
            counter+=1
            
    def set_color_fromRPM(self,rpm):
        if rpm >= self.config["ShiftLights"]["endRPM"]:
            self.handle_limiter()
        else:
            for i in range(self.lightCount):
                # if the rpm is greater or equal the the RPM needed to turn on light
                if rpm >= (self.config["ShiftLights"]["startRPM"] + i * self.rpmStep):
                    #set light to color in config["ShiftLights"]
                        self.set_color_fromConfig(i)
                else: 
                    #set light to be off
                    self.np[i] = (0,0,0)
    
    def setAll_color_fromConfig(self,subKey = "ShiftLights"):
        for id in range(self.lightCount):
            self.set_color_fromConfig(id,subKey=subKey)

    def set_color_fromConfig(self,id,subKey = "ShiftLights"):
        self.set_color(id,self.config["ShiftLights"][subKey][id]["color"])

    def set_configed_limiter_pattern(self,pattern,update=False):
        self.config["ShiftLights"]["LimiterPattern"]["selected"] = pattern
        print(f"Set limiter pattern to: {self.config["ShiftLights"]["LimiterPattern"]["selected"]}")
        
        if update:
            self.sample_limiter()
        
    def set_light_config_color(self,lightsConfig,color):
        lightsConfig["color"]["red"] = color["red"]
        lightsConfig["color"]["green"] = color["green"]
        lightsConfig["color"]["blue"] = color["blue"]
    
    def set_configed_color(self, id, color,subKey = "ShiftLights",update=False):
        self.set_light_config_color(self.config["ShiftLights"][subKey][id],color)
        print(self.config["ShiftLights"][subKey][id])
        
        if update:
            self.setAll_color_fromConfig(subKey)
            self.update()
        
    def set_configed_limiter_color(self,id,color):
        self.set_light_config_color(self.config["ShiftLights"]["LimiterColor"][id],color)
        print(self.config["ShiftLights"]["LimiterColor"][id])
        
    def get_shiftLightConfig(self):
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

        self.init_np() # reinit np so its set to use the new pin

        print(f"Set pin to {self.config["Pins"]["Pins"][pinID]}")
        
    def unassign_pin(self):
        if self.outputPinID != None:
            self.config["ShiftLights"]["pinIDs"] = []
            self.config["Pins"]["Pins"][self.outputPinID]["function"] = ""
            self.outputPinID = None
            self.np = None

    def update(self):
        print("writting to LEDs")
        print([self.np[j] for j in range(len(self.np))])
        
        self.np.write()