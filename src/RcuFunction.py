import asyncio
import json

from asyncServer import async_run_method,run_method
from static import *


class RcuFunction:
    def to_dict(self):
        return {
            RCUFUNC_KEY_ID : self.functionID,
            RCUFUNC_KEY_TYPE : self.functionType,
            self.functionType : {},
        }

    def __init__(
        self,
        functionType,
        functionID,
        init,
        run,
        stop,
        deinit,
        dependencies,
        instance_register,
        resource_handler = None,
    ):
        self.functionType = functionType
        self.functionID = functionID
        self.initFunc = init
        self.run = run
        self.stop = stop 
        self.deinitFunc = deinit
        self.dependencies = dependencies
        self.instance_register = instance_register,
        self.resource_handler = resource_handler
        self.inited = False
        self.sample_task = None
        self.pins = None
        
        

        # for pinFuncName in pinFuncNames:
        #     self.get_funcs_pins(pinFuncName)

    async def init(self):
        if not self.inited:
            try:
                await self.wait_dependencies() # wait for all dependencies to be instanciated
                self.initFunc()
            except PinsNotAssigned:
                pass #pins aren't assigned yet, this may want actioning later?

            self.inited = True
        
    def reinit(self,reinit = True):
        if reinit:
            self.deinit()
            asyncio.run(self.init())
    
    def deinit(self):
        if self.inited:
            self.deinitFunc()
            self.inited = False

    async def wait_dependencies(self):
        for dependency in self.dependencies:
            try:
                while self.instance_register[dependency] == None:
                    # the dependancy hasn't been instancised wait, or handle it here later
                    await asyncio.sleep(DEPENDENCY_SLEEP_TIME_S)
            except Exception as e:
                print(f"Waiting for dependencies has failed, likely due to dependency is {dependency} not being in the instance register {self.instance_register}. The error was: {e}")
                
    def set_assigned_pins(self, pins, reinit = True):
        self.pins = pins
        
        self.reinit(reinit)

    # http methods 
    async def get(self,_):
        return self.to_dict()
    
    async def post(self,data,attr=None):
        print(f"post: {data} | attr {attr}")
        
        
        if None != attr:
            self.set_attr(data,attr)
        else:
        # loop = asyncio.get_event_loop()
        # loop.run_until_complete(self.update_fromDict(data))
            await self.update_fromDict(data)
        return {'message': f"{self.functionID} updated with data"}, 201

    async def put(self,data,attr=None):
        print(f"put: {data}")
        if None != self.sample_task:
            self.sample_task.cancel()
        self.sample_task = async_run_method(self,data)
        
        # await self.sample_task
        
        return {'message': f"Ran {data}"},200
    

