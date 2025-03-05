
PIN_UNASSIGN_NAME = "Unassigned"


class RCU_Function:
    def __init__(self, config,testMode, pinFuncNames):
        self.config = config
        self.testMode = testMode
        self.pinFuncNames = pinFuncNames
        self.assignedPins = []
        for pinFuncName in pinFuncNames:
            self.get_funcs_pins(pinFuncName)


    def set_pin(self, pinID, pinFuncName):
        if pinID == PIN_UNASSIGN_NAME:
            self.unassign_pin()
            return

        # Clear old Pin
        if self.config["ShiftLights"]["pinIDs"] != []:
            self.config["Pins"]["Pins"][self.config["ShiftLights"]["pinIDs"][0]]["function"] = ""

        # Set new pin
        self.config["ShiftLights"]["pinIDs"] = [pinID]
        self.config["Pins"]["Pins"][pinID]["function"] = pinFuncName

        print(f"Set pin to {self.config["Pins"]["Pins"][pinID]}")

    def unassign_pin(self, pinID = None, pin_funcName = None):
        if None != pinID:
            self.config["Pins"]["Pins"][pinID]["function"] = ""

        if None != pin_funcName:
            try:
                self.get_funcs_pins(pin_funcName,0)
            except PinsNotAssigned:
                pass # its already unassigned!
        
    def get_funcs_pins(self, pin_funcName, maxPins = None):
        if None == maxPins:
            maxPins = len(self.pinFuncNames)
        
        # discover assigned pins
        for pin in self.config["Pins"]["Pins"]:
            if pin_funcName in self.config["Pins"]["Pins"][pin]["function"]:
                self.assignedPins.append(self.config["Pins"]["Pins"][pin]["function"])

        if self.assignedPins == []:
            raise PinsNotAssigned

        if len(self.assignedPins) > maxPins:
            print(
                f"{len(self.assignedPins)} is greater than {maxPins}, clearing assignment on additional pins"
            )
            for pin in self.assignedPins[maxPins:]:
                print(f"Clearing {pin}")
                pin["function"] = ""

class PinsNotAssigned(Exception):
    def __init__(self):
        super().__init__("No Pins Allocated for this Function")
