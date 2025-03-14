import os
import re


def find_endpoints_inFrontend(frontEndPath):

    matches = []

    ignores = ["/json", "/^#/,"]

    endpoint_selection_patterns = {"test": re.compile(r'/([^"\']+)["\']')}

    files = [
        f for f in os.listdir(frontEndPath) if f.endswith(".html") or f.endswith(".js")
    ]

    for file in files:
        with open(f"{frontEndPath}/{file}", "r") as f:
            for line in f:
                for key, pattern in endpoint_selection_patterns.items():
                    search = pattern.search(line)
                    if None != search:
                        result = search.group(0).replace('"', "").replace("'", "")
                        if "//" not in result and result.strip() not in ignores:
                            print(result)
                            matches.append(result)

    return matches


def build_fake_http_request(path, body=None, method="OPTIONS"):
    # Ensure method is uppercase
    method = method.upper()

    # Start building the request
    request = f"{method} {path} HTTP/1.1\r\n"
    request += "Host: example.com\r\n"
    request += "User-Agent: MicroPython\r\n"
    request += "Content-Type: application/json\r\n"

    if body:
        request += f"Content-Length: {len(body)}\r\n"
        request += "\r\n" + body  # Separate headers from body with a newline
    else:
        request += "\r\n"  # Just end headers section if no body

    return request


class GenerateTachoSignal:
    def __init__(self, timer, pulsePerRev, pinNum=7, rpm=0):
        from machine import Pin, Timer

        self.Timer = Timer
        self.rpm = rpm
        self.pulsePerRev = pulsePerRev
        self.pinNum = pinNum
        self.timer = timer
        self.calc_period()
        self.pinState = 0
        self.pin = Pin(self.pinNum, Pin.OUT, value=self.pinState)
        self.set_rpm(self.rpm)

    def calc_period(self):
        self.freq = int(
            (self.rpm * self.pulsePerRev * 2) / 60
        )  # 1000 ms in a sec. magic number 2 is bc we need two operations per rpm pulse, setting it high and setting it low
        # print(f"period is {self.freq}ms")

    def toggle_pin(self):
        if self.pinState == 0:
            self.pinState = 1
        else:
            self.pinState = 0
        self.pin.value(self.pinState)

    def set_rpm(self, rpm):
        self.rpm = rpm
        self.calc_period()

        try:
            self.timer.deinit()
        except:
            pass

        self.timer.init(
            freq=self.freq,
            mode=self.Timer.PERIODIC,
            callback=lambda t: self.toggle_pin(),
        )


class Mocked:
    def __init__(self):
        self.runList = []

    def mock_run(self, fname, *args):
        fargs = ""
        for arg in args:
            fargs += f"{arg},"

        fargs = fargs[0:-1]  # remove trailing comma
        self.runList.append(f"{fname}({fargs})")
        
    def assert_mocked_run(self, expectedCall, unittest):
        unittest.assertIn(expectedCall,self.runList)

    def mock_reset(self):
        self.runList = []

class MockedTimer(Mocked):
    PERIODIC = "PERIODIC"
    def __init__(self):
        super().__init__()

    def init(self,**kwargs):
        self.mock_run("init",kwargs)

class MockedShiftLight(Mocked):
    PERIODIC = "PERIODIC"
    def __init__(self):
        super().__init__()

    def setAll_color_fromConfig(self, settingArea):
        self.mock_run("setAll_color_fromConfig", settingArea)

    def update(self):
        self.mock_run("update")

    def sample_pattern(self, settingArea):
        self.mock_run("sample_pattern", settingArea)


class MockedNeoPixel(list):
    def __init__(self, mockedPin, lightCount):
        self.pin = mockedPin  # TODO correct attr name
        super().__init__([(0, 0, 0) for i in range(lightCount)])
        self.mock = Mocked()  # inconsistent but inheritting list is less work

    def write(self):
        self.mock.mock_run("write")


class MockedPin(Mocked):
    OUT = "OUT"
    IN = "IN"
    PULL_DOWN = "PULL_DOWN"
    PinNum = None
    pinMode = None
    pinPull = None

    def __init__(self, PinNum, pinMode, pinPull = None):

        self.PinNum = PinNum  # TODO correct attr name
        self.pinMode = pinMode  # TODO correct attr name
        self.pinPull = pinPull
        super().__init__()
        
    def irq(self, trigger, handler):
        self.mock_run("irq",trigger,handler)

        handler() #actually run the handler to test its a function
