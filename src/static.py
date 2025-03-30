# RCU
CONFIG_PATH = "/workspaces/Resu-Control-Unit/src/data/config.json"
FUNC_ACTIVE_KEY = "activated"

SHIFTLIGHT_TYPE = "ShiftLights"
RPMREADER_TYPE = "RPMReader"
RPMREADER_TACHO_TYPE = "Tacho"
RPMREADER_CAN_TYPE = "CAN"
SERVER_TYPE = "Server"

MOD_NEOPIXEL = "neo"
MOD_PIN = "pin"

KEY_PIN = "Pins"
ID_SEPERATOR = "_"

# ShiftLights

KEY_LIMITER = "Limiter"
KEY_SHIFTLIGHT = "ShiftLights"
KEY_PATTERN = "pattern"
KEY_SELECTED = "selected"
KEY_OPTIIONS = "options"
KEY_COLORS = "colors"
KEY_START_RPM = "startRPM"
KEY_END_RPM = "endRPM"
KEY_LIMITER_PERIOD_S = "period_s"
KEY_BRIGHTNESS = "brightness"
KEY_PULSES_PER_REV = "pulsesPerRev"
KEY_TIMER = "tim"
MOD_TIMER = KEY_TIMER


ASYNC_PAUSE_S = 0.15
MOD_TIMER = KEY_TIMER

PIN_FUNCNAME_SHIFTLIGHTS = KEY_SHIFTLIGHT
PIN_COUNT_SHIFTLIGHTS = 1
LIGHT_COUNT = 15
PATTERN_FLASH = "Flash"
PATTERN_LR = "Left to Right"
PATTERN_RL = "Right to Left"
PATTERN_CI = "Center In"
PATTERN_CO = "Center Out"
PATTERN_SOLID = "Solid"

LIMITER_PATTERNS = [
    PATTERN_FLASH,
    PATTERN_LR,
    PATTERN_RL,
    PATTERN_CI,
    PATTERN_CO,
    PATTERN_SOLID
]

REV_PATTERNS = [
    PATTERN_FLASH,
    PATTERN_LR,
    PATTERN_RL,
    PATTERN_CI,
    PATTERN_CO
]

# RCU_Function
PIN_UNASSIGN_NAME = ""
RCUFUNC_KEY = "RCUFuncs"
RCUFUNC_KEY_ID = "id"
RCUFUNC_KEY_TYPE = "type"
DEPENDENCY_SLEEP_TIME_S = 0.1

# RPMReader

RPM_MODE_TACHO = "TACHO"
RPM_MODE_CAN = "CAN"
RPM_MODES = [
    RPM_MODE_TACHO,
    RPM_MODE_CAN
]
RPM_TACHO_TIMER_PERIOD_MS = 100
PIN_FUNCNAME_RPM = "RPMReader"



class PinAssigned(Exception):
    def __init__(self, pinID):
        super().__init__(f"Pin {pinID} is already assigned to a function")

class PinsNotAssigned(Exception):
    def __init__(self):
        super().__init__("No Pins Allocated for this Function")
