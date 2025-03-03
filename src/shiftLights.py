import neopixel
from machine import Pin

PIN_FUNCNAME_SHIFTLIGHTS = "ShiftLights"
PIN_UNASSIGN_NAME = "Unassigned"

class ShiftLight:
    def __init__(self,config):
        self.config = config
        self.lightCount = len(self.config["ShiftLights"]["ShiftLights"])
        self.rpmStep = (self.config["ShiftLights"]["endRPM"] - self.config["ShiftLights"]["startRPM"])/self.lightCount
        if len(self.config["ShiftLights"]["pinIDs"]) > 0:
            self.outputPinID = self.config["ShiftLights"]["pinIDs"][0]
            self.init_np()
        else:
            self.outputPinID = None
            self.np = None

    def init_np(self):
        self.np = neopixel.NeoPixel(Pin(self.config["Pins"]["Pins"][self.outputPinID]["FirmwareID"], Pin.OUT),self.lightCount)
        
    
    def rgb_to_hsv(self,r, g, b):
        r, g, b = r / 255.0, g / 255.0, b / 255.0
        mx = max(r, g, b)
        mn = min(r, g, b)
        df = mx - mn
        if mx == mn:
            h = 0
        elif mx == r:
            h = (60 * ((g - b) / df) + 360) % 360
        elif mx == g:
            h = (60 * ((b - r) / df) + 120) % 360
        else:
            h = (60 * ((r - g) / df) + 240) % 360
        s = 0 if mx == 0 else df / mx
        v = mx
        return h, s, v

    def hsv_to_rgb(self,h, s, v):
        h = h % 360
        c = v * s
        x = c * (1 - abs((h / 60) % 2 - 1))
        m = v - c
        if 0 <= h < 60:
            r, g, b = c, x, 0
        elif 60 <= h < 120:
            r, g, b = x, c, 0
        elif 120 <= h < 180:
            r, g, b = 0, c, x
        elif 180 <= h < 240:
            r, g, b = 0, x, c
        elif 240 <= h < 300:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x
        return int((r + m) * 255), int((g + m) * 255), int((b + m) * 255)
    
        
    def apply_brightness(self,color,brightness = None):
        if None == brightness:
            brightness = self.config["ShiftLights"]["brightness"]
            
        h, s, v = self.rgb_to_hsv(color["red"], color["green"], color["blue"])
        v *= brightness
        r, g, b = self.hsv_to_rgb(h, s, v)
        
        return {
            "red": int(r),
            "green": int(g),
            "blue": int(b)
        }
        
    def correct_gamma(self,color,gamma = None):
        if None == gamma:
            gamma = self.config["ShiftLights"]["gamma"]
        
        return {
            "red": int(255 * (color["red"] / 255) ** gamma),
            "green": int(255 * (color["green"] / 255) ** gamma),
            "blue": int(255 * (color["blue"] / 255) ** gamma)
        }

    def correct_whiteBalance(self,color, color_factors=None):
        if None == color_factors:
            color_factors = self.config["ShiftLights"]["whiteBalance_factors"]
        return {
            "red": int(color["red"] * color_factors["red"]),
            "green": int(color["green"] * color_factors["green"]),
            "blue": int(color["blue"] * color_factors["blue"])
    }
        
    def setAll_color(self,color):
        for i in range(self.lightCount):
            self.set_color(i,color)
            
    def clear_all(self):
        self.setAll_color({"red":0,"green":0,"blue":0})
            
    def set_color(self, id, color):
        color = self.correct_whiteBalance(color)
        color = self.correct_gamma(color)
        color = self.apply_brightness(color)
        
        self.np[id] = (color["red"],color["green"],color["blue"])
    
    
    # def set_limiter(self):
    #     self.setAll_color(self.config["ShiftLights"]["LimiterColor"]["color"])
        
    def increment_limiter(self, limiterType = None, i=0):
        if None == limiterType or limiterType not in self.config["ShiftLights"]["LimiterPattern"]["patterns"]:
            limiterType = self.config["ShiftLights"]["LimiterPattern"]["selected"]
            print(f"Setting limiter to {limiterType} due to either no value being passed, or an invalid value being passed")

        
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
                        self.set_color_fromConfig(i)
                else: 
                    #set light to be off
                    self.np[i] = (0,0,0)
    
    def setAll_color_fromConfig(self):
        for id in range(self.lightCount):
            self.set_color_fromConfig(id)

    def set_color_fromConfig(self,id):
        self.set_color(id,self.config["ShiftLights"]["ShiftLights"][id]["color"])

        
    def set_limiter_pattern(self,pattern):
        self.config["ShiftLights"]["LimiterPattern"]["Selected"] = pattern
        print(f"Set limiter pattern to: {self.config["ShiftLights"]["LimiterPattern"]["Selected"]}")
        
    def set_light_config_color(self,lightsConfig,color):
        red,green,blue = color
        
        lightsConfig["color"]["red"] = red
        lightsConfig["color"]["green"] = green
        lightsConfig["color"]["blue"] = blue
    
    def set_configed_color(self, id, color,update=False):
        self.set_light_config_color(self.config["ShiftLights"]["ShiftLights"][id],color)
        print(self.config["ShiftLights"]["ShiftLights"][id])
        
        if update:
            self.setAll_color_fromConfig()
            self.update()
        
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

        self.init_np() # reinit np so its set to use the new pin


        print(f"Set pin to {self.config["Pins"]["Pins"][pinID]}")
        
    def unassign_pin(self):
        if self.outputPinID != None:
            self.config["ShiftLights"]["pinIDs"] = []
            self.config["Pins"]["Pins"][self.outputPinID]["function"] = ""
            self.outputPinID = None
            self.np = None
            
            
    def update(self):
        self.np.write()