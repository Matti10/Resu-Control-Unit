import json
import unittest
import testing_utils
import server
import requests
import os
import RCU

MICROPYTHON_EXEC = "/micropython/ports/unix/build-standard/micropython"
SERVER_PATH = "/server.py"
RUN_SERVER_CMD = f"{MICROPYTHON_EXEC} {SERVER_PATH}"

SERVER_ADDRESS = f"http://127.0.0.1:{server.PORT}"

class unitTestAPI(unittest.TestCase):
    def setUp(self):
        self.server = server.RCU_server(testMode=True)
        self.config = self.server.config
        self.configText = json.dumps(self.config)
        # with open(RCU.CONFIG_PATH) as configFile:
        #     self.configText = configFile.read()

        

    def getWebFile_tester(self,route,webfilePath):
        response = requests.get(f"{SERVER_ADDRESS}{route}")
        # print(response.text)

        with open(webfilePath, 'rb') as file:
                content = file.read()

        self.assertEqual(response.content,content)

    def getConfig_tester(self,route,configKey):
        response = requests.get(f"{SERVER_ADDRESS}{route}")

        self.assertEqual(self.config[configKey],json.loads(response.text))
        self.assertIn(response.text,self.configText)


    # ("/ShiftLights", self.get_ShiftLights)
    # ("/ShiftLights", self.post_shiftLight,method="POST")
    # ("/pins", self.get_pins)
    # ("/downloadConfig", self.download_config)
    # ("/uploadConfig", self.upload_config, method="POST")

    # def route_tester(self,route,request,expectedResult,data=None, expectedCode=200):
    #     response = request(route,data)
    #     print(response.text)
    #     response.close()

    def test_getIndex(self):
        self.getWebFile_tester("/",server.INDEX_PATH)

    def test_getFavicon(self):
        self.getWebFile_tester("/favicon.ico",server.FAVICON_PATH)
        

    def test_getWebfiles(self):
        for file in  os.listdir(server.WEB_FILES_PATH):
            self.getWebFile_tester(f"{server.WEB_FILES_ROUTE}/{file}",f"{server.WEB_FILES_PATH}/{file}")

    def test_getShiftLightConfig(self):
        self.getConfig_tester("/ShiftLights","ShiftLights")


if __name__ == "__main__":
    unittest.main()