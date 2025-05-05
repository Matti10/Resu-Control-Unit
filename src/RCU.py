try:
    import ujson as json
except:
    import json

import asyncio
import gc
import re
import sys

import asyncServer
import pins

# import rcuNetwork
import RcuFunction
import rpmReader
import shiftLights
from static import *

if (sys.platform == 'linux'):
    import testing_utils
else:
    import neopixel
    from machine import Pin, Timer

class ResourceAssign:
    RESOURCE_REGISTER = {}
    
    def __init__(self,module_register):
        self.MODULE_REGISTER = module_register
        
    
    def add_resource_type(self,resourceType):
        if resourceType not in self.RESOURCE_REGISTER:
            self.RESOURCE_REGISTER[resourceType] = []
        
    def get_next(self,resourceType):
        """"Return a new resource. ID increments as the list len grows"""
        self.add_resource_type(resourceType)        
        id = len(self.RESOURCE_REGISTER[resourceType])

        nextResource = self.MODULE_REGISTER[resourceType](id)
        
        self.RESOURCE_REGISTER[resourceType].append(
            nextResource
        )
        print(f"Assigned resource {id} | {resourceType}")
        return nextResource
    
        #TODO do i need a way to "return" the resource?? Maybe but right now only for vitual timers, so ceeb. Would need id to NOT just be len of list....
    

class RCU:
    CLASS_REGISTER = {
        # SHIFTLIGHT_TYPE : testing_utils.MockedShiftLight,
        SHIFTLIGHT_TYPE : shiftLights.ShiftLight,
        RPMREADER_TYPE : rpmReader.TachoRpmReader,
        RPMREADER_TYPE : rpmReader.TachoRpmReader,
        RCUFUNCTION_TYPE : RcuFunction.RcuFunction
    }
    INSTANCE_REGISTER = {}
    
    if (sys.platform == 'linux'):
        MODULE_REGISTER = { # Unix/Test mode
            MOD_NEOPIXEL: testing_utils.MockedNeoPixel,
            MOD_PIN: testing_utils.MockedPin,
            MOD_TIMER: testing_utils.MockedTimer,
        }
    else:
        MODULE_REGISTER = { # ESP32
            MOD_NEOPIXEL: neopixel.NeoPixel,
            MOD_PIN: Pin,
            MOD_TIMER: Timer,
        }
    


    def __init__(self):
        self.config = self.import_config()
        
        # init backbone functionality
        # self.RCU_AP = rcuNetwork.rcuAP.build_fromDict(self.config[KEY_AP])
        # self.RCU_AP.start()
        self.RCU_PINS = pins.RcuPins(self.config[KEY_PIN].copy(), self.INSTANCE_REGISTER) # copy the config as the dict needs to be persistent in RcuPins
        self.resourceHandler = ResourceAssign(self.MODULE_REGISTER)

        # instaticate any RCUFuncs from config
        self.addAll_RCUFuncs_fromConfig()

        asyncServer.server.add_resource(self,"/RCU")
        asyncServer.server.add_resource(self.RCU_PINS,"/Pins/<pinNum>")
        asyncServer.add_static_endpoints() # we want to do this after all the other endpoints have been setup - otherwise UI could load before endpoints to build it
        self.config = None
        gc.collect()
        # asyncio.get_event_loop().run_forever()

    
    async def init_RCUFunc(self,id):
        await asyncio.run(self.INSTANCE_REGISTER[id].init())
        
    async def init_all_RCUFuncs(self):
        tasks = [RCUFunc.init() for RCUFunc in self.INSTANCE_REGISTER.values()]
        await asyncio.gather(*tasks)
        
    def add_RCUFunc_fromConfig(self, rcuFuncConfig):
        rcuFuncType = rcuFuncConfig[RCUFUNC_KEY_TYPE]
        print(self.CLASS_REGISTER[rcuFuncType])
        print(self.CLASS_REGISTER[rcuFuncType].build_fromDict)
        RCUFunc = self.CLASS_REGISTER[rcuFuncType].build_fromDict(
            rcuFuncConfig,
            self.INSTANCE_REGISTER,
            self.MODULE_REGISTER,
            self.resourceHandler
        )
        print(RCUFunc)
        self.add_RCUFunc(RCUFunc)
        
    def addAll_RCUFuncs_fromConfig(self):
        try:
            for rcuFuncConfig in self.config[RCUFUNC_KEY].values():
                print(rcuFuncConfig)
                self.add_RCUFunc_fromConfig(rcuFuncConfig)
        except KeyError:
            print("No RCU Funcs in Config")

    def new_RCUFunc(self, rcuFuncType, id = "",add_RCUFunc=True, init_RCUFunc=False):
        if id == "":
            id = self.gen_RCUFunc_id(rcuFuncType)
        
        new_RCUFunc = self.CLASS_REGISTER[rcuFuncType](
            self.INSTANCE_REGISTER,
            self.MODULE_REGISTER,
            id,
            self.resourceHandler
        )    
        
        if add_RCUFunc or init_RCUFunc:
            self.add_RCUFunc(new_RCUFunc, init=init_RCUFunc)
            
        return 
    def add_RCUFunc(self, RCUFunc, init=False):
        print(f"addng rcu func {RCUFunc.functionID}")
        self.INSTANCE_REGISTER[RCUFunc.functionID] = RCUFunc
        
        # assign pins to RCUFuncs
        self.add_RCUFunc_Pins(self.INSTANCE_REGISTER[RCUFunc.functionID], reinit=False)

        if init:
            asyncio.run(self.init_RCUFunc(RCUFunc.functionID))
        
        # add server endpoint
        asyncServer.server.add_resource(self.INSTANCE_REGISTER[RCUFunc.functionID],f"/RCUFuncs/{RCUFunc.functionID}/<attr>")
        
        return self.INSTANCE_REGISTER[RCUFunc.functionID]
    
    def remove_RCUFunc(self,id):
        print(self.INSTANCE_REGISTER)
        if id in self.INSTANCE_REGISTER:
            print(id)
            self.INSTANCE_REGISTER[id].deinit()
            del self.INSTANCE_REGISTER[id]

        print(self.INSTANCE_REGISTER)
        
    
    def add_RCUFunc_Pins(self, RCUFunc, reinit=True):
        try:
            RCUFunc.set_assigned_pins(self.RCU_PINS.get_funcs_pins(RCUFunc.functionID), reinit=reinit)
        except pins.PinsNotAssigned as e:
            pass # at this stage, there isn't nessecarily an issue with no pins being assigned
        
    

    
    def gen_RCUFunc_id(self,rcuFuncType):
        max = -1
        for key in self.INSTANCE_REGISTER.keys():
            try:                
                id = int(key.split(ID_SEPERATOR)[1])
                if id > max:
                    max = id
            except IndexError:
                print(f"invalid ID: {key}")
                #TODO, fix the id?
                
        return f"{rcuFuncType}{ID_SEPERATOR}{max + 1}"
    
    def to_dict(self):
        dict = {}
        # Add RCU funcs config
        dict[RCUFUNC_KEY] = {}#[RCUFunc.to_dict() for RCUFunc in self.INSTANCE_REGISTER.values()]

        for RCUFunc in self.INSTANCE_REGISTER.values():
            dict[RCUFUNC_KEY][RCUFunc.functionID] = RCUFunc.to_dict()
        
        # add Pins
        dict[KEY_PIN] = self.RCU_PINS.to_dict()

        # add AP
        dict[KEY_AP] = "placeholder"
        
        
        return dict
    
    # ------------------ API Endpoints ------------------ #
    def put(self,data):
        try:
            result = asyncServer.run_method(self,data)
            # if its an RCU function, return it as a dict
            if isinstance(result,self.CLASS_REGISTER[RCUFUNCTION_TYPE]):
                return json.dumps(result.to_dict()), 200
            if result == None:
                return "",200
            return result, 200
        except AttributeError as e:
            return {'message':f"function {data[KEY_FUNC]} not found. Error:{e}"}, 404
    
    def patch(self,_):
        try:
            self.export_config()
            return {'message':'Save success'}, 200
        except Exception as e:
            return {'message':f"Failed to Save. Error:{e}"}, 500
        

    @asyncServer.server.route("/pin/<id>",methods=["POST"])
    def set_pin(self,data,id):
        # data = {
        #     funcID : xxxx
        # }
        self.RCU_PINS.unassign_func(data[KEY_FUNC])
        self.RCU_PINS.set_pin(
            id,
            data[KEY_FUNC],
            callback=self.add_RCUFunc_Pins(self.INSTANCE_REGISTER[data[KEY_FUNC]])
        )
        

    # ------------------ Config Managment ------------------ #
    def export_config(self, configPath=CONFIG_PATH):
        self.write_config(self.to_dict(),configPath)
    
    @staticmethod
    def import_config(configPath=CONFIG_PATH):
        with open(configPath, "r") as file:
            return json.load(file)  # Parse JSON file into a dictionary

    @staticmethod
    def write_config(config, configPath=CONFIG_PATH):
        print(f"wrote config to {configPath}\n config is: {config}")
        with open(configPath, "w") as file:
            json.dump(config, file)

    @staticmethod
    def get_rawConfig(configPath=CONFIG_PATH):
        with open(configPath, "r") as file:
            return file.read()

if __name__ == "__main__":
    rcu = RCU()
