import time
import asyncio
from RCU_Function import RCU_Function



SHIFTLIGHT_KEY_LIMITER = "Limiter"
SHIFTLIGHT_KEY_SHIFTLIGHT = "ShiftLights"
SHIFTLIGHT_ASYNC_PAUSE_S = 0.1

PIN_FUNCNAME_SHIFTLIGHTS = SHIFTLIGHT_KEY_SHIFTLIGHT
PIN_COUNT_SHIFTLIGHTS = 1

SHIFTLIGHT_PATTERN_FLASH = "Flash"
SHIFTLIGHT_PATTERN_LR =  "Left to Right"
SHIFTLIGHT_PATTERN_RL =  "Right to Left"
SHIFTLIGHT_PATTERN_CI =  "Center In"
SHIFTLIGHT_PATTERN_CO =  "Center Out"
SHIFTLIGHT_PATTERN_SOLID = "Solid"

class ShiftLight(RCU_Function):
    def __init__(self, config, testMode=False):
        super().__init__(config, testMode, [PIN_FUNCNAME_SHIFTLIGHTS])
        
        self.lightCount = len(self.config[SHIFTLIGHT_KEY_SHIFTLIGHT][SHIFTLIGHT_KEY_SHIFTLIGHT]["colors"])
        self.lightMidPoint = (
            self.lightCount // 2 + (self.lightCount % 2) - 1
        )  # magic number 1 is to account for 0 index
        
        self.patternFuncs = {
            SHIFTLIGHT_KEY_LIMITER : self.init_pattern_fromConfig(SHIFTLIGHT_KEY_LIMITER),
            SHIFTLIGHT_KEY_SHIFTLIGHT : self.init_pattern_fromConfig(SHIFTLIGHT_KEY_SHIFTLIGHT),
        }

        

        self.limiterI = 0
        self.handle_testMode_imports()
        

    
    def init_np(self):
        if self.testMode:
            self.np = [(0,0,0) for i in range(self.lightCount)]
        else:
            #print(self.assignedPins)
            self.np = self.neopixel.NeoPixel(
                self.Pin(self.assignedPins[0]["FirmwareID"], self.Pin.OUT),
                self.lightCount,
            )
            
    def handle_testMode_imports(self):
        if not self.testMode:
            import neopixel
            self.neopixel = neopixel

            from machine import Pin
            self.Pin = Pin

            self.init_np()

    def setAll_color(self, color):
        for i in range(self.lightCount):
            self.set_color(i, color)

    def clear_all(self):
        self.setAll_color({"red": 0, "green": 0, "blue": 0})

    def set_color(self, id, color):
        # color adjustments now done on client side.
        self.np[id] = (color["red"], color["green"], color["blue"])

    def increment_pattern(self, i, subKey):
        if i == 0:
            self.clear_all()
        i = self.patternFuncs[subKey](i)
        
        return i

    def manage_limiterI(self,i,resetValue):
        if i >= resetValue:
            i = 0
        else:
            i += 1            
        return i

    def patternType_LeftRight(self,i):
        #print(f"patternType_LeftRight {i}")
        # left to right
        #print("waving left")
        self.set_color_fromConfig(i, SHIFTLIGHT_KEY_LIMITER)
        return self.manage_limiterI(i,self.lightCount)

    def patternType_RightLeft(self,i):
        #print(f"patternType_RightLeft {i}")
        # right to left
        self.set_color_fromConfig(self.lightCount - (i + 1), SHIFTLIGHT_KEY_LIMITER)
        return self.manage_limiterI(i,self.lightCount)
        

    def patternType_CenterOut(self,i):  # center out
        #print(f"centerOut {i}")
        self.set_color_fromConfig(self.lightMidPoint + i, SHIFTLIGHT_KEY_LIMITER)
        self.set_color_fromConfig(self.lightMidPoint - i, SHIFTLIGHT_KEY_LIMITER)
        return self.manage_limiterI(i,self.lightMidPoint)

    def patternType_CenterIn(self,i):
        #print(f"patternType_CenterIn {i}")
        # center in
        self.set_color_fromConfig(i, SHIFTLIGHT_KEY_LIMITER)
        self.set_color_fromConfig(self.lightCount - (i + 1), SHIFTLIGHT_KEY_LIMITER)
        return self.manage_limiterI(i,self.lightMidPoint)

    def patternType_Flash(self,i):
        #print(f"patternType_Flash {i}")

        if i % 2 == 0:
            self.setAll_color_fromConfig(subKey=SHIFTLIGHT_KEY_LIMITER)
        else:
            self.clear_all()
        return self.manage_limiterI(i,self.lightCount)

    def patternType_Solid(self,i):
        #print(f"patternType_Solid {i}")

        self.setAll_color_fromConfig(subKey=SHIFTLIGHT_KEY_LIMITER)
        return self.manage_limiterI(i,self.lightCount)

    def sample_pattern(self,subKey=SHIFTLIGHT_KEY_SHIFTLIGHT):
        counter = 0
        i = 0
        while counter < self.lightCount:
            #print(f"i:{i}")
            i = self.increment_limiter(
                self.config[SHIFTLIGHT_KEY_SHIFTLIGHT][subKey]["pattern"]["selected"], i
            )
            self.update()
            # TODO make this an interupt so it doesn't lockup the loop
            time.sleep_ms(25)
            counter += 1
            
    def sample_brightness(self,old_brightness,new_brightness=None):
        if None == new_brightness:
            new_brightness = self.config[SHIFTLIGHT_KEY_SHIFTLIGHT]["brightness"]
        
        brightness = 1/old_brightness * new_brightness
        
        #print(brightness)
        
        for light in self.np:
            for color in light:
                color = color * brightness
        self.update()


    def set_i_fromRPM(self, rpm):
        for i in range(1,self.lightCount-1): # start the loop @ 1 - 0 * rpmStep is always < rpm
            # if the rpm is greater or equal the the RPM needed to turn on light
            #print(f"i * self.rpmStep:{i * self.rpmStep} i: {i} rpm: {rpm}")
            
            if rpm < (self.config[SHIFTLIGHT_KEY_SHIFTLIGHT]["startRPM"] + i * self.rpmStep):
                # set light to color in config[SHIFTLIGHT_KEY_SHIFTLIGHT]
                #print(f"returing {i-1}")
                return i-1 #remove the offset 
    
        #print("returning 0")
        return 0 # this should be unreachable, but better safe than sorry :D

    def init_pattern_fromConfig(self,subKey):
        limiterCorr = {
            SHIFTLIGHT_PATTERN_FLASH : {"lightCount": self.lightCount, "func": self.patternType_Flash},
            SHIFTLIGHT_PATTERN_LR : {"lightCount": self.lightCount, "func": self.patternType_LeftRight},
            SHIFTLIGHT_PATTERN_RL : {"lightCount": self.lightCount, "func": self.patternType_RightLeft},
            SHIFTLIGHT_PATTERN_CI : {"lightCount": self.lightMidPoint, "func": self.patternType_CenterIn},
            SHIFTLIGHT_PATTERN_CO : {"lightCount": self.lightMidPoint, "func": self.patternType_CenterOut},
            SHIFTLIGHT_PATTERN_SOLID : {"lightCount": self.lightCount, "func": self.patternType_Solid}
        }

        thisPattern = limiterCorr[self.config[SHIFTLIGHT_KEY_SHIFTLIGHT][subKey]["pattern"]["selected"]]

        if subKey == SHIFTLIGHT_KEY_SHIFTLIGHT:
            self.set_rpmStep(thisPattern["lightCount"])
        return thisPattern["func"]

    def setAll_color_fromConfig(self, subKey=SHIFTLIGHT_KEY_SHIFTLIGHT):
        for id in range(self.lightCount):
            self.set_color_fromConfig(id, subKey=subKey)

    def set_color_fromConfig(self, id, subKey=SHIFTLIGHT_KEY_SHIFTLIGHT):
        self.set_color(id, self.config[SHIFTLIGHT_KEY_SHIFTLIGHT][subKey]["colors"][id]["color"])

    def update(self):
        self.np.write()
        
    def set_rpmStep(self, lightCount):
        self.rpmStep= (
            self.config[SHIFTLIGHT_KEY_SHIFTLIGHT]["endRPM"]
            - self.config[SHIFTLIGHT_KEY_SHIFTLIGHT]["startRPM"]
        ) / lightCount

    # call within a loop to update the shift lights
    async def run(self, rpm_getter):
        while True:
            rpm = rpm_getter()
            if (rpm > self.config[SHIFTLIGHT_KEY_SHIFTLIGHT]["endRPM"]):
                print(f"limiter i (before) {self.limiterI}")
                self.limiterI = self.increment_pattern(i=self.limiterI, subKey=SHIFTLIGHT_KEY_LIMITER)
                await asyncio.sleep(self.config[SHIFTLIGHT_KEY_SHIFTLIGHT][SHIFTLIGHT_KEY_LIMITER]["period_s"])
            elif (rpm > self.config[SHIFTLIGHT_KEY_SHIFTLIGHT]["startRPM"]):
                for i in range(0,self.set_i_fromRPM(rpm)-1):
                    debugI = self.increment_pattern(i=i, subKey=SHIFTLIGHT_KEY_SHIFTLIGHT)
                    print(f"debug i (after) {debugI}")
                await asyncio.sleep(SHIFTLIGHT_ASYNC_PAUSE_S)
            else:
                self.clear_all()
            self.update()