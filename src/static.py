# RCU
ROOT_PATH = "/workspaces/Resu-Control-Unit/src"
# ROOT_PATH = ""
CONFIG_PATH = f"{ROOT_PATH}/data/config.json"
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
KEY_FUNC = "func"
KEY_LIGHT_COUNT = "lightCount"

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
KEY_FIRM_ID = "FirmwareID"

# RPMReader

RPM_MODE_TACHO = "TACHO"
RPM_MODE_CAN = "CAN"
RPM_MODES = [
    RPM_MODE_TACHO,
    RPM_MODE_CAN
]
RPM_TACHO_TIMER_PERIOD_MS = 100
PIN_FUNCNAME_RPM = "RPMReader"

#Networking

KEY_IP = "ip"
KEY_SUB_MASK = "sub"
KEY_GATEWAY = "gate"
KEY_DNS = "dns"
KEY_SSID = "ssid"
KEY_PASSWORD = "password"
KEY_AP = "ap"
KEY_WLAN = "wlan"
AP_DEFAULT_PASSWORD = "1234567890"

# color
KEY_COLOR = "color"
KEY_RED = "r"
KEY_GREEN = "g"
KEY_BLUE = "b"

#server
ROUTE_WEB_FILES = "/webFiles"
WEB_FILES_PATH = f"{ROOT_PATH}/web"
INDEX_PATH = f"{WEB_FILES_PATH}/index.html"
ROUTE_FAVICON = "/favicon.ico"
FAVICON_PATH = f"{WEB_FILES_PATH}/resu-horiz-white.png"
PORT = 8000

ROUTE_CONFIG = "/config"
ROUTE_RPM = "/rpm"
ROUTE_ADDFUNC = "/addFunc"
ROUTE_RMFUNC = "/rmFunc"
KEY_STRING_JSON = "json"
KEY_STRING_INT = "int"
KEY_STRING_STRING = "string"


class PinAssigned(Exception):
    def __init__(self, pinID):
        super().__init__(f"Pin {pinID} is already assigned to a function")

class PinsNotAssigned(Exception):
    def __init__(self):
        super().__init__("No Pins Allocated for this Function")
