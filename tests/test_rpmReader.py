import unittest

import RCU
import rpmReader
import testing_utils


class unitTestTachoRpmReader(unittest.TestCase):
    def setUp(self):
        self.rpmReader = rpmReader.TachoRpmReader(
            config=RCU.import_config(),
            tachoTimer=testing_utils.MockedTimer(),
            pinLib = testing_utils.MockedPin
        )

    def test_init_tacho(self):
        self.assertEqual(self.rpmReader.tachoPin.pinNum,self.rpmReader.assignedPins[0][KEY_FIRM_ID])
        self.assertEqual(self.rpmReader.tachoPin.pinMode,self.rpmReader.Pin.IN)
        self.assertEqual(self.rpmReader.tachoPin.pinPull,self.rpmReader.Pin.PULL_DOWN)

        self.rpmReader.tachoTimer.assert_mocked_run(
            "init({'mode': 'PERIODIC', 'callback':",
            self
        )
        self.rpmReader.tachoTimer.assert_mocked_run(
            f"'period': {rpmReader.RPM_TACHO_TIMER_PERIOD_MS}",
            self
        )
    
    def test_start(self):
        self.rpmReader.start()
        self.rpmReader.tachoPin.assert_mocked_run("irq",self)

    def test_tacho_calc_rpm_callback(self):
        for i in range(0,100000):
            self.rpmReader.pulseCount = i
            self.rpmReader.tacho_calc_rpm_callback("bar")
            self.assertEqual(self.rpmReader.rpm,i*self.rpmReader.tachoRPMScaler)
            self.assertEqual(self.rpmReader.pulseCount,0)

    def test_tacho_irq(self):
        for i in range(1,100000):
            self.rpmReader.tacho_irq("lorem")
            self.assertEqual(i,self.rpmReader.pulseCount)

if __name__ == "__main__":
    unittest.main()
