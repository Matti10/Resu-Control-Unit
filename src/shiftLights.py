import asyncio
import gc
import json
import time

import color

# import RCU
import RcuFunction
from static import *
from utils import deep_copy,set_nested_dict


class ShiftLight(RcuFunction.RcuFunction):
    dependencies = [
        # RCU.ID
    ]
    
    def set_attr(self,data,path):
        keys = path.split(URL_DELIMITER)[1:]
        if KEY_COLOR in path:
            print(type(data))
            if type(data) == list:
                data = [color.Color.build_fromDict(col) for col in data]
            else:
                data = color.Color.build_fromDict(data)
            print("converted to color")
        print(data)
        set_nested_dict(self.config,keys,data)

    #TODO no longer need KWARFS. Literally always interface using dict, converting each time is silly, but needs more invesitgation before naively removing
    @staticmethod
    def build_fromDict(obj, instance_register, module_register, resourceHandler):        
        kwargs = ShiftLight.dictTo_kwargs(obj)
        print(obj[RCUFUNC_KEY_ID])
        return ShiftLight(
            instance_register,
            module_register,
            obj[RCUFUNC_KEY_ID],
            resourceHandler,
            **kwargs
        )
    async def update_fromDict(self,obj):
        # Note to Future me - You cant pass contol back to asyncio here, as it will run server tasks before this (and its parents) have returned!
        kwargs = self.dictTo_kwargs(obj)
        self.config = self.build_config(**kwargs)
        
    @staticmethod
    def dictTo_kwargs(obj):
        # why not send the data as KWARGS????????????
        kwargs = {
            "limiterPattern" : obj[KEY_SHIFTLIGHT][KEY_LIMITER][KEY_PATTERN][KEY_SELECTED],
            "limiterColors" : [color.Color.build_fromDict(col) for col in obj[KEY_SHIFTLIGHT][KEY_LIMITER][KEY_COLORS]], 
            "revPattern" : obj[KEY_SHIFTLIGHT][KEY_SHIFTLIGHT][KEY_PATTERN][KEY_SELECTED], 
            "revColors" : [color.Color.build_fromDict(col) for col in obj[KEY_SHIFTLIGHT][KEY_SHIFTLIGHT][KEY_COLORS]],
            "startRPM" : obj[KEY_SHIFTLIGHT][KEY_START_RPM],
            "endRPM" : obj[KEY_SHIFTLIGHT][KEY_END_RPM],
            "brightness" : obj[KEY_SHIFTLIGHT][KEY_BRIGHTNESS],
            "limiterPeriod_s" : obj[KEY_SHIFTLIGHT][KEY_LIMITER][KEY_LIMITER_PERIOD_S]
        }

        
        return kwargs

    def to_dict(self):
        parentConfig = super().to_dict()
        tempConfig = deep_copy(self.config)
        for section in [KEY_SHIFTLIGHT,KEY_LIMITER]:
            tempConfig[section][KEY_COLORS] = [color.to_dict() for color in self.config[section][KEY_COLORS]]

        parentConfig[self.functionType] = tempConfig
        
        return parentConfig

    def __init__(
        self,
        instance_register,
        module_register,
        id,
        resource_handler,
        **kwargs
    ):
        # Default Values
        kwargs["limiterPattern"] = kwargs.get("limiterPattern",PATTERN_CO)
        kwargs["limiterColors"] = kwargs.get("limiterColors",[color.Color(id=id) for id in range(LIGHT_COUNT)])
        kwargs["revPattern"] = kwargs.get("revPattern",PATTERN_LR)
        kwargs["revColors"] = kwargs.get("revColors",[color.Color(id=id) for id in range(LIGHT_COUNT)])
        kwargs["startRPM"] = kwargs.get("startRPM",0)
        kwargs["endRPM"] = kwargs.get("endRPM",5000)
        kwargs["brightness"] = kwargs.get("brightness",0.5)
        kwargs["limiterPeriod_s"] = kwargs.get("limiterPeriod_s",1)
        
        #build config
        self.config = self.build_config(
            **kwargs
        )
        super().__init__(
            KEY_SHIFTLIGHT,
            id, #id
            self._init,
            self._start,
            self._stop,
            self._deinit,
            self.dependencies,
            instance_register,
            resource_handler=resource_handler
        )
        self.task = None
        # self.rpm_getter = instance_register[RCU.ID].get_rpm
        self.rpm_getter = None
        self.lib_neopixel = module_register[MOD_NEOPIXEL]
        self.lib_Pin = module_register[MOD_PIN]
        self.clearColor = color.Color(0,0,0)
        self.mode = 0
        
    @staticmethod
    def build_config(
        **kwargs
    ): #TODO this could be simplified by defaulting kwargs to current values, would remove the need to send all data
        limiterPattern = kwargs["limiterPattern"]
        limiterColors = kwargs["limiterColors"] 
        revPattern = kwargs["revPattern"]
        revColors = kwargs["revColors"] 
        startRPM = kwargs["startRPM"]  
        endRPM = kwargs["endRPM"]
        brightness = kwargs["brightness"]
        limiterPeriod_s = kwargs["limiterPeriod_s"]
        
        return {
            KEY_SHIFTLIGHT: {
                KEY_COLORS: revColors,
                KEY_PATTERN: {
                    KEY_SELECTED: revPattern,
                    KEY_OPTIIONS: REV_PATTERNS # Is this being stored twice?
                }
            },
            KEY_START_RPM: startRPM,
            KEY_END_RPM: endRPM,
            KEY_BRIGHTNESS: brightness,
            KEY_LIMITER: {
                KEY_LIMITER_PERIOD_S: limiterPeriod_s,
                KEY_PATTERN: {
                    KEY_SELECTED: limiterPattern,
                    KEY_OPTIIONS: LIMITER_PATTERNS # Is this being stored twice?
                },
                KEY_COLORS: limiterColors
            }
        }

    def _deinit(self):
        self.np = None
        self.patternFuncs = None
        gc.collect()

    def _init(self):
        self.lightCount = len(
            self.config[KEY_SHIFTLIGHT][KEY_COLORS]
        )
        self.lightMidPoint = (
            self.lightCount // 2 + (self.lightCount % 2) - 1
        )  # magic number 1 is to account for 0 index
        if self.pins != [] and self.pins != None:
            self.init_np()
            
        self.patternFuncs = {
            KEY_LIMITER: self.init_pattern_fromConfig(
                KEY_LIMITER
            ),
            KEY_SHIFTLIGHT: self.init_pattern_fromConfig(
                KEY_SHIFTLIGHT
            ),
        }
        # setup the timer used to run limiter pattern
        self.limiterTimer = self.resource_handler.get_next(KEY_TIMER)
        self.timerPatternHandler = self.patternFuncs[KEY_LIMITER]
        self.limiterSubkey = KEY_LIMITER # set this so it can be changed by sample functions later. Allows display of non-limiter colors
        self.limiterI = 0
        self.previousRPM = 0
        self.shiftI = 0

    # -------------- Setup  -------------- #
    def init_np(self):
        self.np = self.lib_neopixel(
            self.lib_Pin(self.pins[0][KEY_FIRM_ID], self.lib_Pin.OUT),
            self.lightCount
        )

    def set_rpmStep(self, lightCount):
        self.rpmStep = int(
            (
                self.config[KEY_END_RPM]
                - self.config[KEY_START_RPM]
            )
            / lightCount
        )

    # -------------- Light/Color Handling  -------------- #
    def set_color(self, id, color):
        # color adjustments now done on client side.
        self.np[id] = color.to_npColor()

    def setAll_color(self, color):
        for i in range(self.lightCount):
            self.set_color(i, color)

    def clear_all(self):
        self.setAll_color(self.clearColor)
        
    def lights_are_clear(self):
        clearNp = self.clearColor.to_npColor()
        for light in self.np:
            if light != clearNp:
                return False
        return True

    def set_color_fromConfig(self, id, subKey=KEY_SHIFTLIGHT):
        
        self.set_color(
            id, self.config[subKey][KEY_COLORS][id]
        )

    def setAll_color_fromConfig(self, subKey=KEY_SHIFTLIGHT):
        for id in range(self.lightCount):
            self.set_color_fromConfig(id, subKey=subKey)

    def update(self):
        self.np.write()

    # -------------- Fast color sets for use from server  -------------- #
    #TODO test if this is needed. Ideal world the config is written and shiftlights 
    # re-inited with little enough latency to make good user experince 
    def set_configColor_fromDict(self,id,dict,subKey=KEY_SHIFTLIGHT):
        """Set the color of a light from a dictionary. Dict must follow {r:xxx, g:xxx, b:xxx} format"""
        self.config[subKey][KEY_COLORS][id] =  color.Color(col[KEY_ID],dict[KEY_RED], dict[KEY_GREEN], dict[KEY_GREEN])

    def setAll_configColor_fromDict(self,dict,subKey=KEY_SHIFTLIGHT):
        """Set the color of all lights in the provided dict based on their ID. Dict must be the same format as colors config"""
        ids = dict.keys()
        if len(ids) != self.lightCount:
            print("WARNING: dict doesn't contain a key for each light, not all lights wil be set")
        
        for id in ids:
            self.set_configColor_fromDict(id,dict[id][KEY_COLOR],subKey)

    # -------------- Samples for when Data is Set  -------------- #
    async def sample_color(self, colorDict, subKey, newColor = True):
        self.clear_all()
        self.setAll_color_fromConfig(subKey)
        if newColor:
            newColor = color.Color.build_fromDict(colorDict)
            self.set_color(int(newColor.id),newColor)
        self.update()

    async def sample_pattern(self, pattern=None, period=None, subKey=None,cycle_count = 2):
        print(f"pattern:{pattern}")
        print(f"period:{period}")
        print(f"subKey:{subKey}")
        
        current_pattern = self.patternFuncs[KEY_LIMITER] #backup the current pattern here so we can restore in finally block

        try:
            if subKey is None:
                subKey = KEY_LIMITER
            
            if period is None:
                period = self.config[KEY_LIMITER][KEY_LIMITER_PERIOD_S]

            if pattern is None:
                pattern_handler = self.patternFuncs[subKey]
            else:
                pattern_handler = self.get_patternCorr()[pattern]
                
            print(pattern_handler[KEY_LIGHT_COUNT])
            print(pattern_handler[KEY_FUNC])
            # To sample any pattern, we set the limiters pattern handler to the sample pattern. This then gets called by the timer as part of the normal callback
            self.limiterSubkey = subKey
            self.patternFuncs[KEY_LIMITER] = pattern_handler 
            
            self.enable_limiter(period=period) # enable the limiter with whatever sample period we do or dont set

            await asyncio.sleep(period*pattern_handler[KEY_LIGHT_COUNT]*cycle_count) # await N cycles                
        except Exception as e:
            print(e)
        finally:
            self.patternFuncs[KEY_LIMITER] = current_pattern
            self.limiterSubkey = KEY_LIMITER
            self.disable_limiter()
            self.clear_all()
            self.update()

        
        

    async def sample_brightness(self, _):
        await self.sample_color(None,KEY_SHIFTLIGHT,newColor=False)

    # -------------- Pattern Handling  -------------- #
    def handle_pattern(self, i, subKey):
        if i == 0:
            self.clear_all()
        self.patternFuncs[subKey][KEY_FUNC](i, subKey)

    def get_patternCorr(
        self,
    ):  # hopefully storing like this rather than self.xxxx will mean it doesn't hang around in memory? #TODO confirm this
        return {
            PATTERN_FLASH: {
                KEY_LIGHT_COUNT: self.lightCount,
                KEY_FUNC: self.patternType_Flash,
            },
            PATTERN_LR: {
                KEY_LIGHT_COUNT: self.lightCount,
                KEY_FUNC: self.patternType_LeftRight,
            },
            PATTERN_RL: {
                KEY_LIGHT_COUNT: self.lightCount,
                KEY_FUNC: self.patternType_RightLeft,
            },
            PATTERN_CI: {
                KEY_LIGHT_COUNT: self.lightMidPoint
                + 1,  # magic number. Think of centre in as two half sized lists, that share index 0
                KEY_FUNC: self.patternType_CenterIn,
            },
            PATTERN_CO: {
                KEY_LIGHT_COUNT: self.lightMidPoint
                + 1,  # magic number. Think of centre in as two half sized lists, that share index 0
                KEY_FUNC: self.patternType_CenterOut,
            },
            PATTERN_SOLID: {
                KEY_LIGHT_COUNT: self.lightCount,
                KEY_FUNC: self.patternType_Solid,
            },
        }

    def init_pattern_fromConfig(self, subKey):
        patternCorr = self.get_patternCorr()

        thisPattern = patternCorr[
            self.config[subKey][KEY_PATTERN][KEY_SELECTED]
        ]

        if subKey == KEY_SHIFTLIGHT:
            self.set_rpmStep(thisPattern[KEY_LIGHT_COUNT])

        return thisPattern

    # -------------- Pattern Functions  -------------- #
    def patternType_LeftRight(self, i, subKey):
        self.set_color_fromConfig(i, subKey)

    def patternType_RightLeft(self, i, subKey):
        self.set_color_fromConfig(self.lightCount - (i + 1), subKey)

    def patternType_CenterOut(self, i, subKey):  # center out
        self.set_color_fromConfig(self.lightMidPoint + i, subKey)
        self.set_color_fromConfig(self.lightMidPoint - i, subKey)

    def patternType_CenterIn(self, i, subKey):
        self.set_color_fromConfig(i, subKey)
        self.set_color_fromConfig(self.lightCount - (i + 1), subKey)

    def patternType_Flash(self, i, subKey):
        if i % 2 == 0:
            self.setAll_color_fromConfig(subKey)
        else:
            self.clear_all()

    def patternType_Solid(self, _, subKey):
        self.setAll_color_fromConfig(subKey)

    # -------------- Manage Itteration over Patterns  -------------- #
    def calc_shiftIDirection(self, i, rpm):
        thisStep = i * self.rpmStep
        previousStep = thisStep - self.rpmStep
        diff = rpm - self.previousRPM
        if diff > 0:
            direction = 1
        elif diff < 0:
            direction = -1
        else:
            direction = 0
        #     direction = direction / abs(direction)
        return int(direction), previousStep, thisStep

    def increment_shiftI(self, rpm):
        direction, previousStep, thisStep = self.calc_shiftIDirection(self.shiftI,rpm)
        while not (previousStep < rpm and thisStep >= rpm):
            self.shiftI += direction  # +1 or -1 depending on direction of revs
            direction, previousStep, thisStep = self.calc_shiftIDirection(self.shiftI,rpm)

    def increment_limiterI(self):
        # print(f"i, resetValue {i}, {resetValue}" )
        if self.limiterI >= (self.patternFuncs[KEY_LIMITER][KEY_LIGHT_COUNT] - 1):
            self.limiterI = 0
        else:
            self.limiterI += 1

    
    def limiter_callback(self,_):
        self.handle_pattern(i=self.limiterI, subKey=self.limiterSubkey)
        self.update()
        self.increment_limiterI()
        
    def enable_limiter(self,period=None):
        if None == period:
            self.config[KEY_LIMITER][KEY_LIMITER_PERIOD_S]
        
        period = int(period * 1000)
        
        self.limiterTimer.init(
            mode=self.resource_handler.MODULE_REGISTER[KEY_TIMER].PERIODIC,
            period=period,
            callback=self.limiter_callback
        )

    def disable_limiter(self):
        self.limiterI = 0  # this ensures limiters starts from the start. Only needs to be run once per movement out of limiter...
        self.limiterTimer.deinit()

    # -------------- Main Loop  -------------- #

    def _start(self):
        self.task = asyncio.create_task(self.run())

    def _stop(self):
        if None != self.task:
            self.task.cancel()

    async def run(self):  # TODO ERROR HANDLING FOR TASK
        while True:
            rpm = self.rpm_getter()
        
            if rpm >= self.config[KEY_END_RPM]:
                self.mode = MODE_SHIFTLIGHT_LIMITER
                
                self.enable_limiter()
                await asyncio.sleep(ASYNC_PAUSE_S)
                
            elif rpm > self.config[KEY_START_RPM]:
                if self.mode > MODE_SHIFTLIGHT_LIMITER:
                    self.disable_limiter()
                self.mode = MODE_SHIFTLIGHT_REV
                
                # does this want to be in the a timer interupt?? I.e. self.limiterTimer or the timer used to get rpm?
                self.clear_all()  # TODO remove this and the for loop below and do the same as increment_shiftI so we only set changed lights
                self.increment_shiftI(rpm)
                for i in range(0, self.shiftI):
                    self.handle_pattern(i=i, subKey=KEY_SHIFTLIGHT)
                
                await asyncio.sleep(ASYNC_PAUSE_S)
                
            else:
                if self.mode > MODE_SHIFTLIGHT_OFF:
                    self.shiftI = 0
                await asyncio.sleep(ASYNC_PAUSE_S)
            self.update()
            self.previousRPM = rpm