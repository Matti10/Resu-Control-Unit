from RcuFunction import RcuFunction

RPM_MODE_TACHO = "TACHO"
RPM_MODE_CAN = "CAN"
RPM_TACHO_TIMER_PERIOD_MS = 100
PIN_FUNCNAME_RPM = "RPMReader"

class RpmReader(RcuFunction):
    def __init__(self,config,pinFuncNames):
        self.rpm = 0
        self.config = config
        super().__init__(config,pinFuncNames)

    def get_rpm(self):
        return self.rpm
    
class TachoRpmReader(RpmReader):
    def __init__(self,config,tachoTimer, pinLib):
        super().__init__(config,[PIN_FUNCNAME_RPM])
        self.pulseCount = 0
        self.tachoTimer = tachoTimer
        self.Pin = pinLib  
        self.tachoRPMScaler = (60*(1000/RPM_TACHO_TIMER_PERIOD_MS)) / self.config["RPMReader"]["tachoMode"]["pulsesPerRevolution"]
        self.tachoPin = self.Pin(self.assignedPins[0]["FirmwareID"],self.Pin.IN,self.Pin.PULL_DOWN)
        self.tachoTimer.init(period = RPM_TACHO_TIMER_PERIOD_MS,mode=self.tachoTimer.PERIODIC,callback=self.tacho_calc_rpm_callback)

    def start(self):
        self.tachoPin.irq(trigger=self.Pin.IRQ_RISING, handler=self.tacho_irq)  # Interrupt on rising edge

    def tacho_calc_rpm_callback(self,_):
        self.rpm = self.pulseCount * self.tachoRPMScaler
        self.pulseCount = 0

    def tacho_irq(self,_):
        self.pulseCount += 1

class CanRpmReader(RpmReader):
    def __init____init__(self,config, canLib):
        super().__init__(config,[])