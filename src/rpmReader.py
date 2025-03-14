from RCU_Function import RCU_Function

RPM_MODE_TACHO = "TACHO"
RPM_MODE_CAN = "CAN"
RPM_TACHO_TIMER_PERIOD_MS = 100
PIN_FUNCNAME_RPM = "RPMReader"

class RPMReader(RCU_Function):
    def __init__(self,config,tachoTimer,pin):
        self.rpm = 0
        self.config = config
        self.Pin = pin

        if self.config["RPMReader"]["mode"] == RPM_MODE_TACHO:
            self.pulseCount = 0
            self.tachoTimer = tachoTimer
            self.tachoRPMScaler = (60*(1000/RPM_TACHO_TIMER_PERIOD_MS)) / self.config["RPMReader"]["tachoMode"]["pulsesPerRevolution"]
            super().__init__(config,PIN_FUNCNAME_RPM)
            self.init_tacho()
        else:
            super().__init__(config,None)


    def init_tacho(self):
        self.tachoPin = self.Pin(self.assignedPins[0]["FirmwareID"],self.Pin.IN,self.Pin.PULL_DOWN)
        self.tachoTimer.init(period = RPM_TACHO_TIMER_PERIOD_MS,mode=self.tachoTimer.PERIODIC,callback=self.tacho_calc_rpm_callback)

    def start_tacho(self):
        self.tachoPin.irq(trigger=self.Pin.IRQ_RISING, handler=self.tacho_irq)  # Interrupt on rising edge

    def tacho_calc_rpm_callback(self,_):
        self.rpm = self.pulseCount * self.tachoRPMScaler
        self.pulseCount = 0

    def tacho_irq(self,_):
        self.pulseCount += 1

    def get_rpm(self):
        return self.rpm