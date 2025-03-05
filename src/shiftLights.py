import time

from RCU_Function import RCU_Function

PIN_FUNCNAME_SHIFTLIGHTS = "ShiftLights"
PIN_COUNT_SHIFTLIGHTS = 1


class ShiftLight(RCU_Function):
    def __init__(self, config, testMode=False):
        super().__init__(config, testMode, [PIN_FUNCNAME_SHIFTLIGHTS])

        self.lightCount = len(self.config["ShiftLights"]["ShiftLights"])
        self.rpmStep = (
            self.config["ShiftLights"]["endRPM"]
            - self.config["ShiftLights"]["startRPM"]
        ) / self.lightCount
        self.lightMidPoint = (
            self.lightCount // 2 + (self.lightCount % 2) - 1
        )  # magic number 1 is to account for 0 index

        if not self.testMode:
            import neopixel

            self.neopixel = neopixel

            from machine import Pin

            self.Pin = Pin

            self.init_np()

    def init_np(self):
        if self.testMode:
            self.np = [0 for i in range(self.lightCount)]
        else:
            print(self.assignedPins)
            self.np = self.neopixel.NeoPixel(
                self.Pin(self.assignedPins[0]["FirmwareID"], self.Pin.OUT),
                self.lightCount,
            )

    def setAll_color(self, color):
        for i in range(self.lightCount):
            self.set_color(i, color)

    def clear_all(self):
        self.setAll_color({"red": 0, "green": 0, "blue": 0})

    def set_color(self, id, color):
        # color adjustments now done on client side.
        self.np[id] = (color["red"], color["green"], color["blue"])

    def increment_limiter(self, limiterType=None, i=0):
        # TODO refactor so comparisons aren't permormed every time
        if limiterType == None:
            limiterType = self.config["ShiftLights"]["LimiterPattern"]["selected"]
        print(limiterType)
        if i == 0:
            print("clearing all")
            self.clear_all()

        if limiterType == "Left to Right":  # left to right
            print("waving left")
            self.set_color(i, self.config["ShiftLights"]["LimiterColor"][i]["color"])
        elif limiterType == "Right to Left":  # right to left
            self.set_color(
                self.lightCount - (i + 1),
                self.config["ShiftLights"]["LimiterColor"][self.lightCount - (i + 1)][
                    "color"
                ],
            )
        elif limiterType == "Center Out":  # center out
            self.set_color(
                self.lightMidPoint + i,
                self.config["ShiftLights"]["LimiterColor"][self.lightMidPoint + i][
                    "color"
                ],
            )
            self.set_color(
                self.lightMidPoint - i,
                self.config["ShiftLights"]["LimiterColor"][self.lightMidPoint - i][
                    "color"
                ],
            )
            print(f"lightMidPoint-1:{self.lightMidPoint-1}")
            print(f"lightMidPoint+i:{self.lightMidPoint+i}")
            print(f"lightMidPoint-i:{self.lightMidPoint-i}")
            if i >= self.lightMidPoint:
                i = 0
        elif limiterType == "Center In":  # center in
            self.set_color(i, self.config["ShiftLights"]["LimiterColor"][i]["color"])
            self.set_color(
                self.lightCount - (i + 1),
                self.config["ShiftLights"]["LimiterColor"][self.lightCount - (i + 1)][
                    "color"
                ],
            )

            if i >= self.lightMidPoint:
                i = 0
            # self.setAll_color(self.config["ShiftLights"]["LimiterColor"]["color"])
        elif limiterType == "Flash":
            if i % 2 == 0:
                self.setAll_color_fromConfig(subKey="LimiterColor")
            else:
                self.clear_all()
        else:  # default limiterType == "Solid"
            self.setAll_color_fromConfig(subKey="LimiterColor")

        if i >= self.lightCount:
            i = 0
        else:
            i += 1

        return i

    def handle_limiter(self, limiterType=None):
        # start timer, timing depends on limiter pattern
        if (
            None == limiterType
            or limiterType
            not in self.config["ShiftLights"]["LimiterPattern"]["patterns"]
        ):
            limiterType = self.config["ShiftLights"]["LimiterPattern"]["selected"]
            print(
                f"Setting limiter to {limiterType} due to either no value being passed, or an invalid value being passed"
            )

        i = self.increment_limiter

    def sample_limiter(self):
        counter = 0
        i = 0
        while counter < self.lightCount:
            print(f"i:{i}")
            i = self.increment_limiter(
                self.config["ShiftLights"]["LimiterPattern"]["selected"], i
            )
            self.update()
            # TODO make this an interupt so it doesn't lockup the loop
            time.sleep_ms(25)
            counter += 1

    def set_color_fromRPM(self, rpm):
        if rpm >= self.config["ShiftLights"]["endRPM"]:
            self.handle_limiter()
        else:
            for i in range(self.lightCount):
                # if the rpm is greater or equal the the RPM needed to turn on light
                if rpm >= (self.config["ShiftLights"]["startRPM"] + i * self.rpmStep):
                    # set light to color in config["ShiftLights"]
                    self.set_color_fromConfig(i)
                else:
                    # set light to be off
                    self.np[i] = (0, 0, 0)

    def setAll_color_fromConfig(self, subKey="ShiftLights"):
        for id in range(self.lightCount):
            self.set_color_fromConfig(id, subKey=subKey)

    def set_color_fromConfig(self, id, subKey="ShiftLights"):
        self.set_color(id, self.config["ShiftLights"][subKey][id]["color"])

    def update(self):
        self.np.write()
