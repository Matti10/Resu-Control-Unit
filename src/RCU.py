try:
    import ujson as json
except:
    import json

import asyncio
import gc

import asyncServer
import pins

# import rcuNetwork
import rpmReader
import shiftLights
import testing_utils
from static import *

# import neopixel
# from machine import Pin, Timer



class RCU:
    CLASS_REGISTER = {
        # SHIFTLIGHT_TYPE : testing_utils.MockedShiftLight,
        SHIFTLIGHT_TYPE : shiftLights.ShiftLight,
        RPMREADER_TYPE : rpmReader.TachoRpmReader,
    }
    INSTANCE_REGISTER = {}
    
    MODULE_REGISTER = { # Unix/Test mode
        MOD_NEOPIXEL: testing_utils.MockedNeoPixel,
        MOD_PIN: testing_utils.MockedPin,
        MOD_TIMER: testing_utils.MockedTimer,
    }
    
    # MODULE_REGISTER = { # ESP32
    #     MOD_NEOPIXEL: neopixel.NeoPixel,
    #     MOD_PIN: Pin,
    #     MOD_TIMER: Timer,
    # }
    
    RESOURCE_REGISTER = {
        KEY_TIMER : []
        # KEY_VIRTUAL_TIMER : []
    }

    def __init__(self):
        self.config = self.import_config()
        
        # init backbone functionality
        # self.RCU_AP = rcuNetwork.rcuAP.build_fromDict(self.config[KEY_AP])
        # self.RCU_AP.start()
        self.RCU_PINS = pins.RcuPins(self.config[KEY_PIN].copy()) # copy the config as the dict needs to be persistent in RcuPins
        

        # self.RCU_SERVER = server.RCU_server(self)
        # instaticate any RCUFuncs from config
        self.add_RCUFunc_fromConfig()
        self.add_RCUFunc(SHIFTLIGHT_TYPE)

        self.config = None
        gc.collect()
        asyncio.get_event_loop().run_forever()

    
    async def init_RCUFunc(self,id):
        await asyncio.run(self.INSTANCE_REGISTER[id].init())
        
    async def init_all_RCUFuncs(self):
        tasks = [RCUFunc.init() for RCUFunc in self.INSTANCE_REGISTER.values()]
        await asyncio.gather(*tasks)
        
    def add_RCUFunc_fromConfig(self):
        try: #Pass pins into funcs here? #TODO
            for rcuFuncConfig in self.config[RCUFUNC_KEY]:
                self.add_RCUFunc(
                    rcuFuncConfig[RCUFUNC_KEY_TYPE],
                    rcuFuncConfig[RCUFUNC_KEY_ID]
                )
        except KeyError:
            print("No RCU Funcs in Config adding empty list")

    def add_RCUFunc(self, type, id = None):
        if id == None:
            id = self.gen_RCUFunc_id(type)
            
        print(f"addng rcu func {id}")
        self.INSTANCE_REGISTER[id] = self.CLASS_REGISTER[type](
            self.INSTANCE_REGISTER,
            self.MODULE_REGISTER,
            id,
            self.get_next_timer
        )
        
        # assign pins to RCUFuncs
        self.add_RCUFunc_Pins(self.INSTANCE_REGISTER[id])

        # add server endpoint??
        asyncServer.server.add_resource(self.INSTANCE_REGISTER[id],f"/{id}")
        
        return self.INSTANCE_REGISTER[id]
    
    def remove_RCUFunc(self,id):
        print(self.INSTANCE_REGISTER)
        if id in self.INSTANCE_REGISTER:
            print(id)
            self.INSTANCE_REGISTER[id].deinit()
            del self.INSTANCE_REGISTER[id]

        print(self.INSTANCE_REGISTER)
        
    
    def add_RCUFunc_Pins(self, RCUFunc):
        try:
            RCUFunc.set_assigned_pins(self.RCU_PINS.get_funcs_pins(RCUFunc.functionType), reinit=False)
        except pins.PinsNotAssigned as e:
            pass # at this stage, there isn't nessecarily an issue with no pins being assigned
        
    def get_next_timer(self):
        """"Return a new timer Object. ID increments as the list len grows"""
        nextTimer = self.MODULE_REGISTER[MOD_TIMER](len(self.RESOURCE_REGISTER[KEY_TIMER]))
        self.RESOURCE_REGISTER[KEY_TIMER].append(
            nextTimer
        )

        return nextTimer

    
    def gen_RCUFunc_id(self,type):
        max = -1
        for key in self.INSTANCE_REGISTER.keys():
            try:                
                id = int(key.split(ID_SEPERATOR)[1])
                if id > max:
                    max = id
            except IndexError:
                print(f"invalid ID: {key}")
                #TODO, fix the id?
                
        return f"{type}{ID_SEPERATOR}{max + 1}"
    
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
            
    def export_config(self, configPath=CONFIG_PATH):
        self.write_config(self.to_dict(),configPath)
    
    @staticmethod
    def import_config(configPath=CONFIG_PATH):
        with open(configPath, "r") as file:
            return json.load(file)  # Parse JSON file into a dictionary

    @staticmethod
    def write_config(config, configPath=CONFIG_PATH):
        with open(configPath, "w") as file:
            json.dump(config, file)

    @staticmethod
    def get_rawConfig(configPath=CONFIG_PATH):
        with open(configPath, "r") as file:
            return file.read()

if __name__ == "__main__":
    rcu = RCU()
