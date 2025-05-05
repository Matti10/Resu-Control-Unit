from RcuFunction import RcuFunction
from static import *

# from RCU import CAN_ID



class RpmReader(RcuFunction): 
    def __init__(
        self,
        rpmReaderType,
        functionID,
        _init,
        _run,
        _stop ,
        _deinit,
        dependencies,
        instance_register
    ):
        self.rpm = 0
        self.rpmReaderType = rpmReaderType
        super().__init__(
            RPMREADER_TYPE,
            functionID,
            _init,
            _run,
            _stop,
            _deinit,
            dependencies,
            instance_register
        )

    def to_dict(self):
        parentConfig = super().to_dict()
        parentConfig[RPMREADER_TYPE] = {KEY_OPTIIONS: {
            KEY_SELECTED: self.rpmReaderType,
            KEY_OPTIIONS: [
                RPMREADER_TACHO_TYPE,
                RPMREADER_CAN_TYPE
            ]
        }
        }
        
        return parentConfig

    def get_rpm(self):
        return self.rpm
    
class TachoRpmReader(RpmReader):
    dependencies = []
    @staticmethod
    def build_fromDict(obj, instance_register, module_register, resourceHandler):
        return  TachoRpmReader(
            instance_register,
            module_register,
            obj[RCUFUNC_KEY_ID],
            resourceHandler,
            pulsesPerRevolution=obj[RPMREADER_TYPE][RPMREADER_TACHO_TYPE][KEY_PULSES_PER_REV]
        )
    
    def __init__(
        self,
        instance_register,
        module_register,
        id,
        resourceHandler,
        pulsesPerRevolution = 6
    ):
        self.pulsesPerRevolution = pulsesPerRevolution
        self.lib_pin = module_register[MOD_PIN]
        super().__init__(
            RPMREADER_TACHO_TYPE,
            id, #id
            self._init,
            self._run,
            self._stop,
            self._deinit,
            self.dependencies,
            instance_register
        )
        self.timer_tacho = resourceHandler.get_next(KEY_TIMER)
        self.tachoPin = None
        self.pulseCount = 0
        
    def to_dict(self):
        parentConfig = super().to_dict()
        parentConfig[RPMREADER_TYPE][RPMREADER_TACHO_TYPE] = {
            KEY_PULSES_PER_REV : self.pulsesPerRevolution
        }
        
        return parentConfig
    

    def set_attr(self,data,path):
        print(data)
        print(path)
        if (KEY_PULSES_PER_REV in path):
            self.pulsesPerRevolution = data
            if (self.inited):
                print(self.inited)
                self._deinit()
                self._init()
    
    def _init(self):
        try:
            if self.pulsesPerRevolution == 0:
                self.pulsesPerRevolution = 6 # back to default, zero is no possible and will result in errors
            self.tachoRPMScaler = int(
                (60*(1000/RPM_TACHO_TIMER_PERIOD_MS)) / float(self.pulsesPerRevolution)
            )
            if None != self.pins:
                self.tachoPin = self.lib_pin(
                    self.pins[0][KEY_FIRM_ID],
                    self.lib_pin.IN,
                    self.lib_pin.PULL_DOWN
                )
                self.timer_tacho.init(
                    mode=self.timer_tacho.PERIODIC,
                    period = RPM_TACHO_TIMER_PERIOD_MS,
                    callback=self.tacho_calc_rpm_callback
                )
        except AttributeError:
            raise PinsNotAssigned()


    def _deinit(self):
        self.timer_tacho.deinit()
        self._stop()
        
    def _run(self):
        self.tachoPin.irq(trigger=self.lib_pin.IRQ_RISING, handler=self.tacho_irq)  # Interrupt on rising edge

    def _stop(self):
        if None != self.tachoPin:
            self.tachoPin.irq(trigger=self.lib_pin.IRQ_RISING, handler=lambda:None)
        
    def tacho_calc_rpm_callback(self,_):
        self.rpm = self.pulseCount * self.tachoRPMScaler
        self.pulseCount = 0

    def tacho_irq(self,_):
        self.pulseCount += 1

class CanRpmReader(RpmReader):
    # dependencies = [CAN_ID]
    def __init__(self, instance_register):
        super().__init__(
            "wrong",
            RPMREADER_CAN_TYPE,
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
        