from readline import set_completer
import neopixel
import machine


class RCU_function:
    def __init__(self,pinIDs,name,config):
        self.pins = []
        for pinID in pinIDs:
            self.pins.append(config[pinID])
            
        self.name = name

class ShiftLight(RCU_function):
    def __init__(self,config):
        self.config = config["ShiftLights"]
        self.lightCount = len(self.config["ShiftLights"])
        self.rpmStep = (self.config["endRPM"] - self.config["startRPM"])/self.lightCount
        
        super().__init__(config["Pins"], "ShiftLights", config)

        self.np = neopixel.NeoPixel(self.pins[0],self.lightCount)
        
    def setAll_color(self,color):
        for i in range(self.lightCount):
            self.set_color(i,color)
            
    def clear_all(self):
        self.setAll_color({"red":0,"green":0,"blue":0})
            
    def set_color(self, id, color):
        self.np[id] = (color["red"],color["blue"],color["green"])
        
        
    # def set_limiter(self):
    #     self.setAll_color(self.config["LimiterColor"]["color"])
        
    def increment_limiter(self, limiterType = None, i=0):
        if None == limiterType or limiterType not in self.config["ShiftLights"]["LimiterPattern"]["patterns"]:
            limiterType = self.config["ShiftLights"]["LimiterPattern"]["selected"]

        
        if limiterType == "Wave Left": #left to right
            self.set_color(i,self.config["LimiterColor"]["color"])
        elif limiterType == "Wave Right": #right to left
            self.set_color(self.lightCount - i,self.config["LimiterColor"]["color"])
        elif limiterType == "Wave Center Out": #center out
            mid = self.lightCount // 2 + (self.lightCount % 2)
            
            self.set_color(mid+i,self.config["LimiterColor"]["color"])
            self.set_color(mid-i,self.config["LimiterColor"]["color"])
        elif limiterType == "Wave Center In": #center in
            self.set_color(i,self.config["LimiterColor"]["color"])
            self.set_color(self.lightCount-i,self.config["LimiterColor"]["color"])
            self.setAll_color(self.config["LimiterColor"]["color"])
        elif limiterType == "Flash":
            if i % 2 == 0:
                self.setAll_color(self.config["LimiterColor"]["color"])
            else:
                self.clear_all()
        else:#  limiterType == "Solid"
                self.setAll_color(self.config["LimiterColor"]["color"])

        i += 1
        return i
    
    def handle_limiter(self):
        # start timer, timing depends on limiter pattern
        i = self.increment_limiter
    
    def set_color_fromRPM(self,rpm):
        if rpm >= self.config["endRPM"]:
            self.set_limiter()
        else:
            for i in range(self.lightCount):
                # if the rpm is greater or equal the the RPM needed to turn on light
                if rpm >= (self.config["startRPM"] + i * self.rpmStep):
                    #set light to color in config
                    self.np[i] = (
                        self.config["ShiftLights"][i]["red"],
                        self.config["ShiftLights"][i]["blue"],
                        self.config["ShiftLights"][i]["green"]
                    )
                else: 
                    #set light to be off
                    self.np[i] = (0,0,0)
        
    