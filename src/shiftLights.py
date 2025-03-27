import asyncio
import gc
import json
import time

import RCU
import RcuFunction
import color

KEY_LIMITER = "Limiter"
KEY_SHIFTLIGHT = "ShiftLights"
KEY_PATTERN = "pattern"
KEY_PATTERN_SELECTED = "selected"
KEY_PATTERN_OPTIIONS = "options"
KEY_COLORS = "colors"
KEY_START_RPM = "startRPM"
KEY_END_RPM = "endRPM"
KEY_LIMITER_PERIOD_S = "period_s"
KEY_BRIGHTNESS = "brightness"

ASYNC_PAUSE_S = 0.15

PIN_FUNCNAME_SHIFTLIGHTS = KEY_SHIFTLIGHT
PIN_COUNT_SHIFTLIGHTS = 1
LIGHT_COUNT = 15
PATTERN_FLASH = "Flash"
PATTERN_LR = "Left to Right"
PATTERN_RL = "Right to Left"
PATTERN_CI = "Center In"
PATTERN_CO = "Center Out"
PATTERN_SOLID = "Solid"

LIMITER_PATTERNS = [
    PATTERN_FLASH,
    PATTERN_LR,
    PATTERN_RL,
    PATTERN_CI,
    PATTERN_CO,
    PATTERN_SOLID
]

REV_PATTERNS = [
    PATTERN_FLASH,
    PATTERN_LR,
    PATTERN_RL,
    PATTERN_CI,
    PATTERN_CO
]


class ShiftLight(RcuFunction.RcuFunction):
    dependencies = [
        # RCU.ID
    ]

    @staticmethod
    def from_loadedJson(jsonLoadedObj, instance_register):        
        return ShiftLight(
            instance_register,
            limiterPattern = jsonLoadedObj[KEY_LIMITER][KEY_PATTERN][KEY_PATTERN_SELECTED],
            limiterColors = [color.Color(col[color.KEY_RED],col[color.KEY_GREEN],col[color.KEY_BLUE]) for col in jsonLoadedObj[KEY_LIMITER][KEY_COLORS]], 
            revPattern = jsonLoadedObj[KEY_SHIFTLIGHT][KEY_PATTERN][KEY_PATTERN_SELECTED], 
            revColors = [color.Color(col[color.KEY_RED],col[color.KEY_GREEN],col[color.KEY_BLUE]) for col in jsonLoadedObj[KEY_LIMITER][KEY_COLORS]],
            startRPM = jsonLoadedObj[KEY_START_RPM],
            endRPM = jsonLoadedObj[KEY_END_RPM],
            brightness = jsonLoadedObj[KEY_BRIGHTNESS],
            limiterPeriod_s = jsonLoadedObj[KEY_LIMITER_PERIOD_S]
        )

    def to_dict(self):
        parentConfig = super().to_dict()
        tempConfig = self.config.copy()
        for colorList in [tempConfig[KEY_SHIFTLIGHT],tempConfig[KEY_LIMITER]]:
            for color in colorList:
                color = color.to_dict()

        parentConfig[self.functionType] = tempConfig
        
        return parentConfig

    def __init__(
        self,
        instance_register,
        limiterPattern = PATTERN_CO,
        limiterColors = [color.Color(id) for id in range(LIGHT_COUNT)],
        revPattern = PATTERN_LR,
        revColors = [color.Color(id) for id in range(LIGHT_COUNT)],
        startRPM = 0,
        endRPM = 5000,
        brightness = 0.5,
        limiterPeriod_s = 0.25,
        lib_neoPixel = None,
        lib_pin = None
    ):
        self.config = {
            KEY_SHIFTLIGHT: {
                KEY_COLORS: revColors,
                KEY_PATTERN: {
                    KEY_PATTERN_SELECTED: revPattern,
                    KEY_PATTERN_OPTIIONS: REV_PATTERNS
                }
            },
            KEY_START_RPM: startRPM,
            KEY_END_RPM: endRPM,
            KEY_BRIGHTNESS: brightness,
            KEY_LIMITER: {
                KEY_LIMITER_PERIOD_S: limiterPeriod_s,
                KEY_PATTERN: {
                    KEY_PATTERN_SELECTED: limiterPattern,
                    KEY_PATTERN_OPTIIONS: LIMITER_PATTERNS
                },
                KEY_COLORS: limiterColors
            }
        }
        super().__init__(
            KEY_SHIFTLIGHT,
            10, #id
            self._init,
            self._start,
            self._stop,
            self._deinit,
            self.dependencies,
            instance_register
        )
        self.task = None
        # self.rpm_getter = instance_register[RCU.ID].get_rpm
        self.rpm_getter = None
        self.lib_neopixel = lib_neoPixel
        self.lib_Pin = lib_pin
        self.handle_mocked_imports()

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

        self.init_np()
        self.patternFuncs = {
            KEY_LIMITER: self.init_pattern_fromConfig(
                KEY_LIMITER
            ),
            KEY_SHIFTLIGHT: self.init_pattern_fromConfig(
                KEY_SHIFTLIGHT
            ),
        }

        self.limiterI = 0
        self.previousRPM = 0
        self.shiftI = 0

    # -------------- Setup  -------------- #
    def handle_mocked_imports(self):
        if self.lib_neopixel == None:
            from neopixlel import NeoPixel
            self.lib_neopixel = NeoPixel
        if self.lib_pin == None:
            from machine import Pin
            self.lib_pin = Pin
            
    def init_np(self):
        # print(self.assignedPins)
        self.np = self.lib_neopixel(
            self.lib_Pin(self.assignedPins[0]["FirmwareID"], self.lib_Pin.OUT),
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
        self.np[id] = (col[color.KEY_RED], col[KEY_GREEN], col[color.KEY_GREEN])

    def setAll_color(self, color):
        for i in range(self.lightCount):
            self.set_color(i, color)

    def clear_all(self):
        self.setAll_color({color.KEY_RED: 0, KEY_GREEN: 0, color.KEY_GREEN: 0})

    def set_color_fromConfig(self, id, subKey=KEY_SHIFTLIGHT):
        self.set_color(
            id, self.config[subKey][KEY_COLORS][id]["color"]
        )

    def setAll_color_fromConfig(self, subKey=KEY_SHIFTLIGHT):
        for id in range(self.lightCount):
            self.set_color_fromConfig(id, subKey=subKey)

    def update(self):
        self.np.write()

    # -------------- Samples for when Data is Set  -------------- #
    def sample_pattern(self, subKey=KEY_SHIFTLIGHT):
        counter = 0
        i = 0
        while counter < self.lightCount:
            # print(f"i:{i}")
            i = self.handle_pattern(
                self.config[subKey][KEY_PATTERN][KEY_PATTERN_SELECTED], i
            )
            self.update()
            # TODO make this an interupt so it doesn't lockup the loop. Mocking the getRPM func would be a good way to do it
            time.sleep_ms(25)
            counter += 1

    def sample_brightness(self, old_brightness, new_brightness=None):
        if None == new_brightness:
            new_brightness = self.config[KEY_BRIGHTNESS]

        brightness = 1 / old_brightness * new_brightness

        for light in self.np:
            for color in light:
                color = color * brightness
        self.update()

    # -------------- Pattern Handling  -------------- #
    def handle_pattern(self, i, subKey):
        if i == 0:
            self.clear_all()
        self.patternFuncs[subKey]["func"](i, subKey)

    def get_patternCorr(
        self,
    ):  # hopefully storing like this rather than self.xxxx will mean it doesn't hang around in memory? #TODO confirm this
        return {
            PATTERN_FLASH: {
                "lightCount": self.lightCount,
                "func": self.patternType_Flash,
            },
            PATTERN_LR: {
                "lightCount": self.lightCount,
                "func": self.patternType_LeftRight,
            },
            PATTERN_RL: {
                "lightCount": self.lightCount,
                "func": self.patternType_RightLeft,
            },
            PATTERN_CI: {
                "lightCount": self.lightMidPoint
                + 1,  # magic number. Think of centre in as two half sized lists, that share index 0
                "func": self.patternType_CenterIn,
            },
            PATTERN_CO: {
                "lightCount": self.lightMidPoint
                + 1,  # magic number. Think of centre in as two half sized lists, that share index 0
                "func": self.patternType_CenterOut,
            },
            PATTERN_SOLID: {
                "lightCount": self.lightCount,
                "func": self.patternType_Solid,
            },
        }

    def init_pattern_fromConfig(self, subKey):
        patternCorr = self.get_patternCorr()

        thisPattern = patternCorr[
            self.config[subKey][KEY_PATTERN][KEY_PATTERN_SELECTED]
        ]

        if subKey == KEY_SHIFTLIGHT:
            self.set_rpmStep(thisPattern["lightCount"])
        return thisPattern

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

    def increment_limiterI(self, i, resetValue):
        # print(f"i, resetValue {i}, {resetValue}" )
        if i >= resetValue:
            i = 0
        else:
            i += 1
        return i

    # -------------- Main Loop  -------------- #
    # call within a loop to update the shift lights

    def _start(self):
        self.task = asyncio.create_task(self.run())

    def _stop(self):
        if None != self.task:
            self.task.cancel()

    async def run(self):  # TODO ERROR HANDLING FOR TASK
        while True:
            rpm = self.rpm_getter()
            
            if rpm >= self.config[KEY_END_RPM]:
                # print(f"limiter i (before) {self.limiterI}")
                self.handle_pattern(i=self.limiterI, subKey=KEY_LIMITER)
                self.limiterI = self.increment_limiterI(
                    self.limiterI,
                    self.patternFuncs[KEY_LIMITER]["lightCount"] - 1,
                )
                await asyncio.sleep(
                    self.config[KEY_LIMITER][
                        KEY_LIMITER_PERIOD_S
                    ]
                )
            elif rpm > self.config[KEY_START_RPM]:
                self.clear_all()  # TODO remove this and the for loop below and do the same as increment_shiftI so we only set changed lights
                print("e")
                self.increment_shiftI(rpm)
                for i in range(0, self.shiftI):
                    self.handle_pattern(i=i, subKey=KEY_SHIFTLIGHT)
                self.limiterI = 0  # this ensures limiters starts from the start. Only needs to be run once per movement out of limiter...
                await asyncio.sleep(ASYNC_PAUSE_S)
            else:
                self.shiftI = 0
                await asyncio.sleep(ASYNC_PAUSE_S)
            self.update()
            self.previousRPM = rpm