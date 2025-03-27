PIN_UNASSIGN_NAME = "Unassigned"
RCUFUNC_KEY = "RCUFuncs"
RCUFUNC_KEY_ID = "id"
RCUFUNC_KEY_TYPE = "type"
DEPENDENCY_SLEEP_TIME_S = 0.1

import asyncio


class RcuFunction:
    def to_dict(self):
        return {
        RCUFUNC_KEY_ID : self.functionID,
        RCUFUNC_KEY_TYPE : self.functionType,
        self.functionType : {},
    }

    def __init__(self, functionType, functionID, init, run, stop, deinit, dependencies, instance_register,pinFuncNames=None, config =None):
        self.config = config
        if pinFuncNames == None:
            pinFuncName = [functionType]
        self.pinFuncNames = pinFuncNames
        self.assignedPins = []
        self.functionType = functionType
        self.functionID = functionID
        self.initFunc = init
        self.run = run
        self.stop = stop 
        self.deinit = deinit
        self.dependencies = dependencies
        self.instance_register = instance_register


        # for pinFuncName in pinFuncNames:
        #     self.get_funcs_pins(pinFuncName)

    async def init(self):
        await self.wait_dependencies() # wait for all dependencies to be instanciated
        self.initFunc()

    async def wait_dependencies(self):
        for dependency in self.dependencies:
            try:
                while self.instance_register[dependency] == None:
                    # the dependancy hasn't been instancised wait, or handle it here later
                    asyncio.sleep(DEPENDENCY_SLEEP_TIME_S)
            except Exception as e:
                print(f"Waiting for dependencies has failed, likely due to dependency is {dependency} not being in the instance register {self.instance_register}. The error was: {e}")

    # def set_pin(self, pinID, pinFuncName):
    #     if pinID == PIN_UNASSIGN_NAME:
    #         self.unassign_pin()
    #         return

    #     # Clear old Pin
    #     if self.config["ShiftLights"]["pinIDs"] != []:
    #         self.config["Pins"]["Pins"][self.config["ShiftLights"]["pinIDs"][0]][
    #             "function"
    #         ] = ""

    #     # Set new pin
    #     self.config["ShiftLights"]["pinIDs"] = [pinID]
    #     self.config["Pins"]["Pins"][pinID]["function"] = pinFuncName


    # def unassign_pin(self, pinID=None, pin_funcName=None):
    #     if None != pinID:
    #         self.config["Pins"]["Pins"][pinID]["function"] = ""

    #     if None != pin_funcName:
    #         try:
    #             self.get_funcs_pins(pin_funcName, 0)
    #         except PinsNotAssigned:
    #             pass  # its already unassigned!

    # def get_funcs_pins(self, pin_funcName, maxPins=None):
    #     if None == maxPins:
    #         maxPins = len(self.pinFuncNames)

    #     # discover assigned pins
    #     for pin in self.config["Pins"]["Pins"]:
    #         if pin_funcName == self.config["Pins"]["Pins"][pin]["function"]:
    #             self.assignedPins.append(self.config["Pins"]["Pins"][pin])

    #     if self.assignedPins == []:
    #         raise PinsNotAssigned

    #     if len(self.assignedPins) > maxPins:
    #         print(
    #             f"{len(self.assignedPins)} is greater than {maxPins}, clearing assignment on additional pins"
    #         )
    #         for pin in self.assignedPins[maxPins:]:
    #             print(f"Clearing {pin}")
    #             pin["function"] = ""
                
        
    


class PinsNotAssigned(Exception):
    def __init__(self):
        super().__init__("No Pins Allocated for this Function")
