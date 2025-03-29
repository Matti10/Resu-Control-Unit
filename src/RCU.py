try:
    import ujson as json
except:
    import json

import rpmReader
import server
import shiftLights
import gc
import testing_utils
from static import *
import asyncio





class RCU:
    CLASS_REGISTER = {
        SHIFTLIGHT_TYPE : shiftLights.ShiftLight,
        RPMREADER_TYPE : rpmReader.TachoRpmReader,
        SERVER_TYPE : server.RCU_server
    }
    INSTANCE_REGISTER = {
        # SERVER_TYPE : CLASS_REGISTER[SERVER_TYPE](testMode=True)
    }
    
    MODULE_REGISTER = { # Unix/Test mode
        MOD_NEOPIXEL: testing_utils.MockedNeoPixel,
        MOD_PIN: testing_utils.MockedPin
    }

    def __init__(self):
        self.config = self.import_config()
        
        # self.add_RCUFunc(SHIFTLIGHT_TYPE)
        
        
        self.config = None
        gc.collect()
    
    async def init_RCUFunc(self,id):
        await asyncio.run(self.INSTANCE_REGISTER[id].init())
        
    async def init_all_RCUFuncs(self):
        tasks = [RCUFunc.init() for RCUFunc in self.INSTANCE_REGISTER.values()]
        await asyncio.gather(*tasks)
        
    def add_RCUFunc_fromConfig(self):
        try:
            for rcuFuncConfig in self.config[RCUFUNC_KEY]:
                self.add_RCUFunc(
                    rcuFuncConfig[RCUFUNC_KEY_TYPE],
                    rcuFuncConfig[RCUFUNC_KEY_ID]
                )
        except KeyError:
            print("No RCU Funcs in Config adding empty list")
            self.config[RCUFUNC_KEY] = []

    def add_RCUFunc(self, type, id = None):
        if id == None:
            id = self.gen_RCUFunc_id(type)
            
        self.INSTANCE_REGISTER[id] = self.CLASS_REGISTER[type](
            self.INSTANCE_REGISTER,
            self.MODULE_REGISTER,
            id
        )
        
        return self.INSTANCE_REGISTER[id]
    
    def rm_RCUFunc(self,id):
        self.INSTANCE_REGISTER.pop(id,None)
    
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
        dict[RCUFUNC_KEY] = [RCUFunc.to_dict() for RCUFunc in self.INSTANCE_REGISTER.values()]            
        
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
