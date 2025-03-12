import unittest

import RCU
import shiftLights
import testing_utils


class unitTestShiftLights(unittest.TestCase):
    def setUp(self):
        self.shift = shiftLights.ShiftLight(
            config=RCU.import_config(),
            testMode=True,
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

    def assert_all_clear(self):
        for i in range(self.shift.lightCount):
            self.assertEqual(self.shift.np[i], (0, 0, 0))

    def test_init_np(self):
        # this is really testing the Mocked NeoPixel/Pin, but good to confirm its mocked correctly
        self.shift.init_np()
        self.assertEqual(len(self.shift.np), 15)
        self.assertEqual(len(self.shift.np), self.shift.lightCount)
        for item in self.shift.np:
            self.assertEqual(item, (0, 0, 0))

        self.assertEqual(self.shift.np.pin.pinMode, self.shift.Pin.OUT)

    def test_handle_testMode_imports(self):
        pass  # func is only to handle test mode

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

    def test_increment_pattern(self):
        for key in [
            shiftLights.SHIFTLIGHT_KEY_LIMITER,
            shiftLights.SHIFTLIGHT_KEY_SHIFTLIGHT,
        ]:  # run twice to valiate it clears
            for i in range(self.shift.lightCount + 1):
                self.shift.increment_pattern(i, key)
                if i == 0:
                    self.assert_all_clear()
                raise Exception("#TODO implement this")


if __name__ == "__main__":
    unittest.main()
