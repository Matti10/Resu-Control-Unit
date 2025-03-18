import asyncio
import time

from RcuFunction import RcuFunction

SHIFTLIGHT_KEY_LIMITER = "Limiter"
SHIFTLIGHT_KEY_SHIFTLIGHT = "ShiftLights"
SHIFTLIGHT_ASYNC_PAUSE_S = 0.15

PIN_FUNCNAME_SHIFTLIGHTS = SHIFTLIGHT_KEY_SHIFTLIGHT
PIN_COUNT_SHIFTLIGHTS = 1

SHIFTLIGHT_PATTERN_FLASH = "Flash"
SHIFTLIGHT_PATTERN_LR = "Left to Right"
SHIFTLIGHT_PATTERN_RL = "Right to Left"
SHIFTLIGHT_PATTERN_CI = "Center In"
SHIFTLIGHT_PATTERN_CO = "Center Out"
SHIFTLIGHT_PATTERN_SOLID = "Solid"


class ShiftLight(RcuFunction):
    def __init__(self, config, neoPixel, pin):
        super().__init__(config, [PIN_FUNCNAME_SHIFTLIGHTS])
        self.neopixel = neoPixel
        self.Pin = pin
        self.lightCount = len(
            self.config[SHIFTLIGHT_KEY_SHIFTLIGHT][SHIFTLIGHT_KEY_SHIFTLIGHT]["colors"]
        )
        self.lightMidPoint = (
            self.lightCount // 2 + (self.lightCount % 2) - 1
        )  # magic number 1 is to account for 0 index

        self.init_np()
        self.patternFuncs = {
            SHIFTLIGHT_KEY_LIMITER: self.init_pattern_fromConfig(
                SHIFTLIGHT_KEY_LIMITER
            ),
            SHIFTLIGHT_KEY_SHIFTLIGHT: self.init_pattern_fromConfig(
                SHIFTLIGHT_KEY_SHIFTLIGHT
            ),
        }

        self.limiterI = 0
        self.previousRPM = 0
        self.shiftI = 0

    # -------------- Setup  -------------- #
    def init_np(self):
        # print(self.assignedPins)
        self.np = self.neopixel(
            self.Pin(self.assignedPins[0]["FirmwareID"], self.Pin.OUT),
            self.lightCount,
        )

    def set_rpmStep(self, lightCount):
        self.rpmStep = int(
            (
                self.config[SHIFTLIGHT_KEY_SHIFTLIGHT]["endRPM"]
                - self.config[SHIFTLIGHT_KEY_SHIFTLIGHT]["startRPM"]
            )
            / lightCount
        )

    # -------------- Light/Color Handling  -------------- #
    def set_color(self, id, color):
        # color adjustments now done on client side.
        self.np[id] = (color["r"], color["g"], color["b"])

    def setAll_color(self, color):
        for i in range(self.lightCount):
            self.set_color(i, color)

    def clear_all(self):
        self.setAll_color({"r": 0, "g": 0, "b": 0})

    def set_color_fromConfig(self, id, subKey=SHIFTLIGHT_KEY_SHIFTLIGHT):
        self.set_color(
            id, self.config[SHIFTLIGHT_KEY_SHIFTLIGHT][subKey]["colors"][id]["color"]
        )

    def setAll_color_fromConfig(self, subKey=SHIFTLIGHT_KEY_SHIFTLIGHT):
        for id in range(self.lightCount):
            self.set_color_fromConfig(id, subKey=subKey)

    def update(self):
        self.np.write()

    # -------------- Samples for when Data is Set  -------------- #
    def sample_pattern(self, subKey=SHIFTLIGHT_KEY_SHIFTLIGHT):
        counter = 0
        i = 0
        while counter < self.lightCount:
            # print(f"i:{i}")
            i = self.handle_pattern(
                self.config[SHIFTLIGHT_KEY_SHIFTLIGHT][subKey]["pattern"]["selected"], i
            )
            self.update()
            # TODO make this an interupt so it doesn't lockup the loop. Mocking the getRPM func would be a good way to do it
            time.sleep_ms(25)
            counter += 1

    def sample_brightness(self, old_brightness, new_brightness=None):
        if None == new_brightness:
            new_brightness = self.config[SHIFTLIGHT_KEY_SHIFTLIGHT]["brightness"]

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
            SHIFTLIGHT_PATTERN_FLASH: {
                "lightCount": self.lightCount,
                "func": self.patternType_Flash,
            },
            SHIFTLIGHT_PATTERN_LR: {
                "lightCount": self.lightCount,
                "func": self.patternType_LeftRight,
            },
            SHIFTLIGHT_PATTERN_RL: {
                "lightCount": self.lightCount,
                "func": self.patternType_RightLeft,
            },
            SHIFTLIGHT_PATTERN_CI: {
                "lightCount": self.lightMidPoint
                + 1,  # magic number. Think of centre in as two half sized lists, that share index 0
                "func": self.patternType_CenterIn,
            },
            SHIFTLIGHT_PATTERN_CO: {
                "lightCount": self.lightMidPoint
                + 1,  # magic number. Think of centre in as two half sized lists, that share index 0
                "func": self.patternType_CenterOut,
            },
            SHIFTLIGHT_PATTERN_SOLID: {
                "lightCount": self.lightCount,
                "func": self.patternType_Solid,
            },
        }

    def init_pattern_fromConfig(self, subKey):
        patternCorr = self.get_patternCorr()

        thisPattern = patternCorr[
            self.config[SHIFTLIGHT_KEY_SHIFTLIGHT][subKey]["pattern"]["selected"]
        ]

        if subKey == SHIFTLIGHT_KEY_SHIFTLIGHT:
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
    async def run(self, rpm_getter):  # TODO ERROR HANDLING FOR TASK
        while True:
            rpm = rpm_getter()
            
            if rpm >= self.config[SHIFTLIGHT_KEY_SHIFTLIGHT]["endRPM"]:
                # print(f"limiter i (before) {self.limiterI}")
                self.handle_pattern(i=self.limiterI, subKey=SHIFTLIGHT_KEY_LIMITER)
                self.limiterI = self.increment_limiterI(
                    self.limiterI,
                    self.patternFuncs[SHIFTLIGHT_KEY_LIMITER]["lightCount"] - 1,
                )
                await asyncio.sleep(
                    self.config[SHIFTLIGHT_KEY_SHIFTLIGHT][SHIFTLIGHT_KEY_LIMITER][
                        "period_s"
                    ]
                )
            elif rpm > self.config[SHIFTLIGHT_KEY_SHIFTLIGHT]["startRPM"]:
                self.clear_all()  # TODO remove this and the for loop below and do the same as increment_shiftI so we only set changed lights
                print("e")
                self.increment_shiftI(rpm)
                for i in range(0, self.shiftI):
                    self.handle_pattern(i=i, subKey=SHIFTLIGHT_KEY_SHIFTLIGHT)
                self.limiterI = 0  # this ensures limiters starts from the start. Only needs to be run once per movement out of limiter...
                await asyncio.sleep(SHIFTLIGHT_ASYNC_PAUSE_S)
            else:
                self.shiftI = 0
                await asyncio.sleep(SHIFTLIGHT_ASYNC_PAUSE_S)
            self.update()
            self.previousRPM = rpm