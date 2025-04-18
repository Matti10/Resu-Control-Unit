import random
import unittest

import RCU
import shiftLights
import testing_utils


def some_mocked_pattern_func(i, subKey):
    global mockedPatternFuncData
    mockedPatternFuncData = {"subKey": subKey, "i": i}


class unitTestShiftLights(unittest.TestCase):
    def setUp(self):
        self.shift = shiftLights.ShiftLight(
            config=RCU.import_config(),
            neoPixel=testing_utils.MockedNeoPixel,
            pin=testing_utils.MockedPin,
        )
        self.testColors = [
            {"r": 255, "g": 255, "b": 255},
            {"r": 165, "g": 25, "b": 25},
            {"r": 155, "g": 155, "b": 2},
            {"r": 5, "g": 225, "b": 4},
            {"r": 245, "g": 235, "b": 3},
            {"r": 205, "g": 5, "b": 0},
        ]

        self.correctPatternItteration = {
            "Flash": {
                "0": ["x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x"],
                "1": ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                "2": ["x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x"],
                "3": ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                "4": ["x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x"],
                "5": ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                "6": ["x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x"],
                "7": ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                "8": ["x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x"],
                "9": ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                "10": ["x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x"],
                "11": ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                "12": ["x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x"],
                "13": ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                "14": ["x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x"], 
                "15": ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"]
            },
            "Left to Right": {
                "0": ["x", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                "1": ["x", "x", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                "2": ["x", "x", "x", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                "3": ["x", "x", "x", "x", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                "4": ["x", "x", "x", "x", "x", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                "5": ["x", "x", "x", "x", "x", "x", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
                "6": ["x", "x", "x", "x", "x", "x", "x", "0", "0", "0", "0", "0", "0", "0", "0"],
                "7": ["x", "x", "x", "x", "x", "x", "x", "x", "0", "0", "0", "0", "0", "0", "0"],
                "8": ["x", "x", "x", "x", "x", "x", "x", "x", "x", "0", "0", "0", "0", "0", "0"],
                "9": ["x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "0", "0", "0", "0", "0"],
                "10": ["x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "0", "0", "0", "0"],
                "11": ["x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "0", "0", "0"],
                "12": ["x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "0", "0"],
                "13": ["x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "0"],
                "14": ["x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x"],
                "15": ["x", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"]
            }, 
            "Right to Left": {
                "0": ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "x"],
                "1": ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "x", "x"],
                "2": ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "x", "x", "x"],
                "3": ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "x", "x", "x", "x"],
                "4": ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "x", "x", "x", "x", "x"],
                "5": ["0", "0", "0", "0", "0", "0", "0", "0", "0", "x", "x", "x", "x", "x", "x"],
                "6": ["0", "0", "0", "0", "0", "0", "0", "0", "x", "x", "x", "x", "x", "x", "x"],
                "7": ["0", "0", "0", "0", "0", "0", "0", "x", "x", "x", "x", "x", "x", "x", "x"],
                "8": ["0", "0", "0", "0", "0", "0", "x", "x", "x", "x", "x", "x", "x", "x", "x"],
                "9": ["0", "0", "0", "0", "0", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x"],
                "10": ["0", "0", "0", "0", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x"],
                "11": ["0", "0", "0", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x"],
                "12": ["0", "0", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x"],
                "13": ["0", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x"],
                "14": ["x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x"],
                "15": ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "x"]
            }, 
            "Center In": {
                "0": ["x", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "x"],
                "1": ["x", "x", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "x", "x"],
                "2": ["x", "x", "x", "0", "0", "0", "0", "0", "0", "0", "0", "0", "x", "x", "x"],
                "3": ["x", "x", "x", "x", "0", "0", "0", "0", "0", "0", "0", "x", "x", "x", "x"],
                "4": ["x", "x", "x", "x", "x", "0", "0", "0", "0", "0", "x", "x", "x", "x", "x"],
                "5": ["x", "x", "x", "x", "x", "x", "0", "0", "0", "x", "x", "x", "x", "x", "x"],
                "6": ["x", "x", "x", "x", "x", "x", "x", "0", "x", "x", "x", "x", "x", "x", "x"],
                "7": ["x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x"],
                "8": ["x", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "x"]
            }, 
            "Center Out": {
                "0": ["0", "0", "0", "0", "0", "0", "0", "x", "0", "0", "0", "0", "0", "0", "0"],
                "1": ["0", "0", "0", "0", "0", "0", "x", "x", "x", "0", "0", "0", "0", "0", "0"],
                "2": ["0", "0", "0", "0", "0", "x", "x", "x", "x", "x", "0", "0", "0", "0", "0"],
                "3": ["0", "0", "0", "0", "x", "x", "x", "x", "x", "x", "x", "0", "0", "0", "0"],
                "4": ["0", "0", "0", "x", "x", "x", "x", "x", "x", "x", "x", "x", "0", "0", "0"],
                "5": ["0", "0", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "0", "0"],
                "6": ["0", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "0"],
                "7": ["x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x"], 
                "8": ["0", "0", "0", "0", "0", "0", "0", "x", "0", "0", "0", "0", "0", "0", "0"]
            }, 
            "Solid": {
                "0": ["x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x"],
                "1": ["x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x"],
                "2": ["x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x"],
                "3": ["x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x"],
                "4": ["x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x"],
                "5": ["x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x"],
                "6": ["x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x"],
                "7": ["x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x"],
                "8": ["x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x"],
                "9": ["x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x"],
                "10": ["x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x"],
                "11": ["x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x"],
                "12": ["x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x"],
                "13": ["x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x"],
                "14": ["x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x"],
                "15": ["x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x"]
            }
        }

    def assert_all_clear(self):
        for i in range(self.shift.lightCount):
            self.assertEqual(self.shift.np[i], (0, 0, 0))

    def assert_all_configed_color(self, subKey):
        for i in range(self.shift.lightCount):
            self.assertEqual(
                self.shift.np[i],
                (
                    self.shift.config[shiftLights.SHIFTLIGHT_KEY_SHIFTLIGHT][subKey][
                        "colors"
                    ][i][KEY_COLOR]["r"],
                    self.shift.config[shiftLights.SHIFTLIGHT_KEY_SHIFTLIGHT][subKey][
                        "colors"
                    ][i][KEY_COLOR]["g"],
                    self.shift.config[shiftLights.SHIFTLIGHT_KEY_SHIFTLIGHT][subKey][
                        "colors"
                    ][i][KEY_COLOR]["b"],
                ),
            )

    def assert_patternData(self, patternData):
        self.assertTrue(type(patternData[KEY_LIGHT_COUNT]) == type(2))
        self.assertTrue(
            patternData[KEY_LIGHT_COUNT] == self.shift.lightCount
            or patternData[KEY_LIGHT_COUNT] == (self.shift.lightMidPoint + 1)
        )
        self.assertTrue(type(patternData[KEY_FUNC]) == type(self.shift.get_patternCorr))

    def assert_np_changed(self,function, *args):
        # check func actually runs & does something
        npBefore = self.shift.np[:]
        function(*args)
        # print(f"\n{npBefore}\n{self.shift.np}\n")
        # print(npBefore == self.shift.np)
        # print(f"args:{args}")
        self.assertFalse(npBefore == self.shift.np)

    def test_init_np(self):
        # this is really testing the Mocked NeoPixel/Pin, but good to confirm it's mocked correctly
        self.shift.init_np()
        self.assertEqual(len(self.shift.np), 15)
        self.assertEqual(len(self.shift.np), self.shift.lightCount)
        for item in self.shift.np:
            self.assertEqual(item, (0, 0, 0))

        self.assertEqual(self.shift.np.pin.pinMode, self.shift.Pin.OUT)

    def test_handle_testMode_imports(self):
        pass  # func is only to handle test mode

    def test_set_rpmStep(self):
        for i in range(1, 50):
            self.shift.set_rpmStep(i)
            result = self.shift.rpmStep
            self.assertTrue(type(result) == type(1))  # check its returning an int
            self.assertAlmostEqual(
                result,
                (
                    (
                        self.shift.config[shiftLights.SHIFTLIGHT_KEY_SHIFTLIGHT]["endRPM"]
                        - self.shift.config[shiftLights.SHIFTLIGHT_KEY_SHIFTLIGHT]["startRPM"]
                    )
                    / i
                ),
                -1,
            )
            # test that the max rpm value that can be set from RPM step is within allowableRPMDiff of the set RPM
            maxRPM = self.shift.config[shiftLights.SHIFTLIGHT_KEY_SHIFTLIGHT]["endRPM"]
            maxRPMStep = result * i
            allowableRPMDiff = 1.5 * i
            if maxRPMStep < maxRPM:
                self.assertTrue(maxRPMStep >= (maxRPM - allowableRPMDiff))
            elif maxRPMStep > maxRPM:
                self.assertTrue(maxRPMStep <= (maxRPM + allowableRPMDiff))
            else:
                self.assertAlmostEqual(maxRPMStep, maxRPM, 0)

    def test_set_color(self):
        for i in range(self.shift.lightCount):
            for color in self.testColors:
                self.shift.set_color(i, color)
                self.assertEqual(self.shift.np[i][0], color["r"])
                self.assertEqual(self.shift.np[i][1], color["g"])
                self.assertEqual(self.shift.np[i][2], color["b"])

        self.shift.clear_all()

    def test_set_allColor(self):
        for color in self.testColors:
            self.shift.setAll_color(color)
            for i in range(self.shift.lightCount):
                self.assertEqual(self.shift.np[i][0], color["r"])
                self.assertEqual(self.shift.np[i][1], color["g"])
                self.assertEqual(self.shift.np[i][2], color["b"])

        self.shift.clear_all()

    def test_clear_all(self):
        self.shift.clear_all()
        self.assert_all_clear()

    def test_set_color_fromConfig(self):
        self.shift.clear_all()
        for key in [
            shiftLights.SHIFTLIGHT_KEY_LIMITER,
            shiftLights.SHIFTLIGHT_KEY_SHIFTLIGHT,
        ]:
            for i in range(self.shift.lightCount):
                self.shift.set_color_fromConfig(i, key)
            self.assert_all_configed_color(key)

    def test_setAll_color_fromConfig(self):
        for key in [
            shiftLights.SHIFTLIGHT_KEY_LIMITER,
            shiftLights.SHIFTLIGHT_KEY_SHIFTLIGHT,
        ]:
            self.shift.setAll_color_fromConfig(key)
            self.assert_all_configed_color(key)

    def test_update(self):
        self.shift.update()
        self.shift.np.mock.assert_mocked_run("write()",self)

        self.shift.np.mock.mock_reset()

    def test_handle_pattern(self):
        for key in [
            shiftLights.SHIFTLIGHT_KEY_LIMITER,
            shiftLights.SHIFTLIGHT_KEY_SHIFTLIGHT,
        ]:
            self.shift.patternFuncs[key][KEY_FUNC] = some_mocked_pattern_func
            for i in range(0, 50):
                self.shift.handle_pattern(i, key)
                result = mockedPatternFuncData
                self.assertEqual(result["i"], i)
                self.assertEqual(result["subKey"], key)
                if i == 0:
                    self.assert_all_clear()

    def test_get_patternCorr(self):
        patternCorr = self.shift.get_patternCorr()
        for key in [
            shiftLights.SHIFTLIGHT_KEY_LIMITER,
            shiftLights.SHIFTLIGHT_KEY_SHIFTLIGHT,
        ]:
            for pattern in self.shift.config[shiftLights.SHIFTLIGHT_KEY_SHIFTLIGHT][
                key
            ]["pattern"]["options"]:
                self.assertIn(pattern, patternCorr.keys())
                self.assert_patternData(patternCorr[pattern])

    def test_init_pattern_fromConfig(self):
        for key in [
            shiftLights.SHIFTLIGHT_KEY_LIMITER,
            shiftLights.SHIFTLIGHT_KEY_SHIFTLIGHT,
        ]:
            for pattern in self.shift.config[shiftLights.SHIFTLIGHT_KEY_SHIFTLIGHT][
                key
            ]["pattern"]["options"]:
                self.shift.config[shiftLights.SHIFTLIGHT_KEY_SHIFTLIGHT][key][
                    "selected"
                ] = pattern
                self.shift.init_pattern_fromConfig(key)
                self.assert_patternData(
                    self.shift.patternFuncs[key]
                )  # check pattern data is valid

                # check func actually runs & does something
                self.shift.clear_all()
                self.assert_np_changed(self.shift.patternFuncs[key][KEY_FUNC],self.shift.patternFuncs[key][KEY_LIGHT_COUNT] - 1, key)
                

        self.shift.clear_all()

    def test_patternType_all(self):
        patternCorr = self.shift.get_patternCorr()
        for key in [
            shiftLights.SHIFTLIGHT_KEY_LIMITER,
            shiftLights.SHIFTLIGHT_KEY_SHIFTLIGHT,
        ]:
            for pattern in self.shift.config[shiftLights.SHIFTLIGHT_KEY_SHIFTLIGHT][key]["pattern"]["options"]:
                # print(pattern)
                for i in range(0,patternCorr[pattern][KEY_LIGHT_COUNT]):
                    if pattern != shiftLights.SHIFTLIGHT_PATTERN_SOLID:
                        self.assert_np_changed(patternCorr[pattern][KEY_FUNC],i,key)
                    else:
                        patternCorr[pattern][KEY_FUNC](i,key)
                    # print(f"\"{i}\":\"{self.shift.np}\"")
                    for lightIndex in range(self.shift.lightCount):
                        thisLightCorrect = self.correctPatternItteration[pattern][str(i)][lightIndex]
                        thisLight = self.shift.np[lightIndex]
                        # print(f"\n{pattern}@{i}\n{thisLight}\n{thisLightCorrect}\n")
                        
                        if thisLight == (0, 0, 0):
                            self.assertEqual("0",thisLightCorrect)
                        else:
                            self.assertEqual("x",thisLightCorrect)

                self.shift.clear_all()

    def test_calc_shiftIDirection(self):
        rpms = [0,0,0] + [random.randint(-10,20000) for i in range(10000)]
        
        for i in range(self.shift.lightCount + 1):
            for rpm in rpms:
                direction,previousStep,thisStep = self.shift.calc_shiftIDirection(i, rpm)
                self.assertAlmostEqual(thisStep, i * self.shift.rpmStep)
                self.assertAlmostEqual(previousStep, thisStep - self.shift.rpmStep)
                self.assertTrue(type(direction) == type(-1))  # check its returning an int
                self.assertTrue(type(thisStep) == type(1))  # check its returning an int
                self.assertTrue(type(previousStep) == type(1))  # check its returning an int

                if rpm > self.shift.previousRPM:
                    self.assertEqual(direction,1)
                elif rpm < self.shift.previousRPM:
                    self.assertEqual(direction,-1)
                else:
                    self.assertEqual(direction,0)

                self.shift.previousRPM = rpm

    def test_increment_shiftI(self):
        rpms = [0,0,0] + [random.randint(-10,self.shift.config[shiftLights.SHIFTLIGHT_KEY_SHIFTLIGHT]["endRPM"]) for i in range(10000)]
        
        for rpm in rpms:
            # direction, previousStep, thisStep = self.shift.calc_shiftIDirection(self.shift.shiftI,rpm)
            self.shift.increment_shiftI(rpm)
            self.assertTrue((self.shift.rpmStep * self.shift.shiftI) >= rpm)
            self.assertTrue((self.shift.rpmStep * (self.shift.shiftI - 1)) < rpm)
            self.shift.previousRPM = rpm

    def test_increment_limiterI(self):
        lastI = 0
        for resetVal in [random.randint(1,30) for e in range(100)]:
            i = 0
            for e in range(0,1000):
                self.shift.increment_limiterI(i,resetVal)
                self.assertTrue(i <= resetVal)
                self.assertTrue(i == (lastI+1) or i == 0)
                lastI = i

if __name__ == "__main__":
    unittest.main()
