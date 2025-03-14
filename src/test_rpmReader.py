import unittest

import RCU
import rpmReader
import testing_utils


class unitTestRpmReader(unittest.TestCase):
    def setUp(self):
        self.rpmReader = rpmReader.RPMReader(
            config=RCU.import_config(),
            tachoTimer=testing_utils.MockedTimer(),
            pin = testing_utils.MockedPin
        )

    def test_init_tacho(self):
        self.rpmReader.init_tacho()

        self.assertEqual(self.rpmReader.Pin.PinNum,self.rpmReader.assignedPins[0]["FirmwareID"])
        self.assertEqual(self.rpmReader.Pin.PinMode,"IN")
        self.assertEqual(self.rpmReader.Pin.pinPull,self.rpmReader.assignedPins[0]["FirmwareID"])

        self.rpmReader.tachoTimer.assert_mocked_run(
            f"init({rpmReader.RPM_TACHO_TIMER_PERIOD_MS},IRQ_RISING,tacho_irq)",
            self
        )

if __name__ == "__main__":
    unittest.main()
