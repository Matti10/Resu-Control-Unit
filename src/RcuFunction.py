from static import *
import asyncio


class RcuFunction:
    def to_dict(self):
        return {
        RCUFUNC_KEY_ID : self.functionID,
        RCUFUNC_KEY_TYPE : self.functionType,
        self.functionType : {},
    }

    def __init__(self, functionType, functionID, init, run, stop, deinit, dependencies, instance_register):
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



