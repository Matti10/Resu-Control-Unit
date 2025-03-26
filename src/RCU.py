try:
    import ujson as json
except:
    import json

import rpmReader
import server
import shiftLights

CONFIG_PATH = "/workspaces/Resu-Control-Unit/src/data/config.json"
FUNC_ACTIVE_KEY = "activated"

SHIFTLIGHT_ID = "ShiftLights"
RPMREADER_ID = "RPMReader"
SERVER_ID = "Server"



class RCU:
    CLASS_REGISTER = {
        SHIFTLIGHT_ID : shiftLights.ShiftLight,
        RPMREADER_ID : rpmReader.RpmReader,
        SERVER_ID : server.RCU_server
    }
    INSTANCE_REGISTER = {
        SHIFTLIGHT_ID : None,
        RPMREADER_ID : None,
        SERVER_ID : None
    }

    def __init__(self):
        self.config = self.import_config()
        
        self.find_activated_functions()
        
    def add_function()

    def instaciate_active_functions(self):
        for activeFunc in self.activeFunctions:
            self.INSTANCE_REGISTER[activeFunc] = self.CLASS_REGISTER[activeFunc](self.config)

    def init_active_functions(self):


    def find_activated_functions(self):
        self.activeFunctions = []
        for funcID in self.config.keys():
            if FUNC_ACTIVE_KEY in funcID.keys():
                if funcID[FUNC_ACTIVE_KEY]: # if its active
                    self.activeFunctions.append(funcID)
        

    @staticmethod
    def import_config(configPath=CONFIG_PATH):
        with open(configPath, "r") as file:
            return json.load(file)  # Parse JSON file into a dictionary

    @staticmethod
    def export_config(config, configPath=CONFIG_PATH):
        with open(configPath, "w") as file:
            json.dump(config, file)

    @staticmethod
    def get_rawConfig(configPath=CONFIG_PATH):
        with open(configPath, "r") as file:
            return file.read()
