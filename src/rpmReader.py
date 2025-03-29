from RcuFunction import RcuFunction
# from RCU import CAN_ID

RPM_MODE_TACHO = "TACHO"
RPM_MODE_CAN = "CAN"
RPM_TACHO_TIMER_PERIOD_MS = 100
PIN_FUNCNAME_RPM = "RPMReader"

class RpmReader(RcuFunction):
    async def __init__(self,config,pinFuncNames,init, run, stop, deinit, dependencies, instance_register):
        self.rpm = 0
        self.config = config
        super().__init__(
            config,
            pinFuncNames,
            init,
            run,
            stop,
            deinit,
            dependencies,
            instance_register
        )

    def get_rpm(self):
        return self.rpm
    
class TachoRpmReader(RpmReader):
    dependencies = []
    async def __init__(self,config,tachoTimer, instance_register, lib_pin = None):
        self.lib_pin = lib_pin
        self.handle_mocked_imports()

        await super().__init__(
            config,
            [PIN_FUNCNAME_RPM],
            self._init,
            self._run,
            self._stop,
            self._clear,
            self.dependencies,
            instance_register
        )

        self.pulseCount = 0
        self.tachoTimer = tachoTimer
    
    def _init(self):
        self.tachoRPMScaler = (60*(1000/RPM_TACHO_TIMER_PERIOD_MS)) / self.config["RPMReader"]["tachoMode"]["pulsesPerRevolution"]
        self.tachoPin = self.lib_pin(self.assignedPins[0]["FirmwareID"],self.lib_pin.IN,self.lib_pin.PULL_DOWN)
        self.tachoTimer.init(period = RPM_TACHO_TIMER_PERIOD_MS,mode=self.tachoTimer.PERIODIC,callback=self.tacho_calc_rpm_callback)

    def _clear(self):
        # No way to deinit pins, they just get inited "over"
        self.tachoTimer.deinit()

    def _run(self):
        self.tachoPin.irq(trigger=self.lib_pin.IRQ_RISING, handler=self.tacho_irq)  # Interrupt on rising edge

    def _stop(self):
        pass #the gravy train never stops

    def handle_mocked_imports(self):
        if self.lib_pin == None:
            from machine import Pin
            self.lib_pin = Pin

    def tacho_calc_rpm_callback(self,_):
        self.rpm = self.pulseCount * self.tachoRPMScaler
        self.pulseCount = 0

    def tacho_irq(self,_):
        self.pulseCount += 1

class CanRpmReader(RpmReader):
    # dependencies = [CAN_ID]
    async def __init__(self,config, instance_register):
        await super().__init__(
            config,
            [PIN_FUNCNAME_RPM],
            self._init,
            self._run,
            self._stop,
            self._clear,
            self.dependencies,
            instance_register
        )

    
    def _init(self):
        raise Exception("#TODO")

    def _clear(self):
        raise Exception("#TODO")


    def _run(self):
        raise Exception("#TODO")

    def _stop(self):
        raise Exception("#TODO")
        