REPO_ROOT = "/workspaces/Resu-Control-Unit"

import gc
import os

gc.enable()
os.chdir(f"{REPO_ROOT}/src")

import json
import unittest

import RCU
import server
import testing_utils

# once in production this needs to be a serperate folder that files are copied into....


class unitTestServer(unittest.TestCase):
    def setUp(self):
        self.server = server.RCU_server(
            testMode=True, shiftLights=testing_utils.MockedShiftLight()
        )

    def test_frontend_routes_exist(self):
        usedRoutes = testing_utils.find_endpoints_inFrontend(
            frontEndPath=f"{REPO_ROOT}/src/web"
        )

        serverRoutes = [route["path"] for route in self.server.server._routes]

        # print(f"Following routes found in UI: {usedRoutes}")
        # print(f"Following routes found in Server: {serverRoutes}")

        for route in usedRoutes:
            rootRoute = "/" + route.split("/")[1]
            self.assertIn(
                rootRoute,
                serverRoutes,
                f"{rootRoute} (from {route}) is not in server routes ({self.server.server._routes})",
            )

        gc.collect()

    def test_file_exists(self):
        self.assertTrue(
            self.server.file_exists(__file__)
        )  # test the file we're running exists
        self.assertFalse(
            self.server.file_exists("/some/garbage/path")
        )  # test the file we're running exists

        gc.collect()

    def test_serve_file(
        self,
        validFiles=[__file__, server.INDEX_PATH, server.FAVICON_PATH],
        invalidFiles=["wrong", "/looks/right/but/is/wrong.lol"],
    ):

        for file in validFiles:
            result = self.server.serve_file(file)
            result = [item for item in result]

            result = b"".join(result)

            with open(file, "rb") as file:
                content = file.read()

            self.assertEqual(
                content[0:1000], result[0:1000]
            )  # only sample the first 1000 bytes due to RAM constraints
            gc.collect()

        for file in invalidFiles:
            try:
                result = self.server.serve_file(file)
            except Exception as e:
                self.assertEqual(type(e).__name__, "RouteNotFound")

        gc.collect()

    def map_all_configKeys(self, d, path, testFunc, childArgs=None):
        print(f"\n\n--------------START--------------")
        print(f"input is: {d}")
        if isinstance(d, dict):
            for key, value in d.items():
                newPath = f"{path}/{key}"
                self.map_all_configKeys(
                    d[key], newPath, testFunc, childArgs=childArgs
                )  # Recursively process the value
                testFunc(newPath, value, childArgs)
        elif isinstance(d, list):
            for i in range(0, len(d) - 1):
                newPath = f"{path}/[{i}]"
                self.map_all_configKeys(
                    d[i], newPath, testFunc, childArgs=childArgs
                )  # Recursively process list items
                testFunc(newPath, d[i], childArgs)

    def test_serve_json(self):
        testObj = {
            "test": 1,
            "test1": "1",
            "test2": {"test3": [1, 2, 3]},
            "test4": False,
        }

        realObj = self.server.serve_json(testObj)

        print(realObj)
        print(type(realObj))

        self.assertEqual(testObj, json.loads(realObj.decode()))

        gc.collect()

    def test_get_config(self):
        def get_config_tester(path, this, _):
            print(f"Testing config path: {path}")  # Print the key
            request = testing_utils.build_fake_http_request(path=path)
            print(f"request:{request}")
            result = self.server.get_config(request)
            result = result.decode()
            print(f"result is: {result}, actual data is: {this}")
            self.assertEqual(json.loads(result), this)

        self.map_all_configKeys(self.server.config, "/config", get_config_tester)
        gc.collect()

    def test_set_config(self):
        testData = [
            {"test": "Lorem Ipsum"},
            {"test": 0},
            {"test": False},
            {"test": {"test": {"test": "Lorem Ipsum"}}},
            {
                "test": [
                    {"test": "Lorem Ipsum"},
                    {"test": "Lorem Ipsum"},
                    {"test": "Lorem Ipsum"},
                ]
            },
        ]

        def set_config_tester(path, this, test):
            body = json.dumps(test)
            print(f"body:{body}")
            request = testing_utils.build_fake_http_request(path=path, body=body)
            print(f"request:{request}")
            result = self.server.set_config(request=request)

            self.assertEqual(
                json.loads(self.server.get_config(request=request).decode()),
                test["test"],
            )

        for test in testData:
            self.map_all_configKeys(
                self.server.config, "/config", set_config_tester, test
            )
            self.server.config = RCU.import_config()  # reset config as we just broke it
            gc.collect()

    def test_get_favicon(self):
        self.test_serve_file(validFiles=[server.FAVICON_PATH], invalidFiles=[])
        gc.collect()

    def test_get_webFiles(self):
        for file in os.listdir(server.WEB_FILES_PATH):
            fileData = []
            if "index" in file:
                request = testing_utils.build_fake_http_request("/")
            else:
                request = testing_utils.build_fake_http_request(
                    f"{server.ROUTE_WEB_FILES}/{file}"
                )

            result = self.server.get_webFiles(request)
            with open(f"{server.WEB_FILES_PATH}/{file}", "rb") as f:
                while chunk := f.read(512):  # Read in chunks (512 bytes)
                    # Send each chunk
                    fileData.append(chunk)
            self.assertEqual(fileData, result)
            gc.collect()

    def test_post_shiftLight(self):
        tests = [
            {
                "route": "/ShiftLights/ShiftLights/colors/[10]/color",
                "shouldCall": ["setAll_color_fromConfig(ShiftLights)", "update()"],
                "testData": {"test": 3000},
            },
            {
                "route": "/ShiftLights/Limiter/colors/[10]/color",
                "shouldCall": ["setAll_color_fromConfig(Limiter)", "update()"],
                "testData": {"test": 3000},
            },
            {
                "route": "/ShiftLights/ShiftLights/pattern/selected",
                "shouldCall": ["sample_pattern(ShiftLights)"],
                "testData": {"test": "Lorem Ipsum"},
            },
            {
                "route": "/ShiftLights/Limiter/pattern/selected",
                "shouldCall": ["sample_pattern(Limiter)"],
                "testData": {"test": "Lorem Ipsum"},
            },
            {
                "route": "/ShiftLights/brightness",
                "shouldCall": ["setAll_color_fromConfig(ShiftLights)", "update()"],
                "testData": {"test": 1.5},
            },
        ]

        for test in tests:
            request = testing_utils.build_fake_http_request(
                test["route"], body=json.dumps(test["testData"])
            )
            self.server.post_shiftLight(request)

            # test that the functions used to show changes on physical lights are called
            # for expectedCall in test["shouldCall"]:
            # remeber the MockedShiftLight is being used here
            self.assertEqual(test["shouldCall"], self.server.ShiftLights.runList)

            self.assertEqual(
                json.loads(self.server.get_config(request)),
                test["testData"]["test"],
            )

            self.server.ShiftLights.runList = []  # clear it for the next round of tests

        self.server.config = RCU.import_config()  # reset config as we just broke it
        gc.collect()

    def test_download_file(self, filePath=f"{server.WEB_FILES_PATH}/ui.js"):
        with open(filePath, "r") as file:
            data = file.read()

        sent = self.server.download_file(data, "test.test")

        self.assertEqual(sent, data)

    def test_download_config(self):
        self.test_download_file(RCU.CONFIG_PATH)

    def test_upload_config(self):
        # Simulate an HTTP multipart request
        data = {"setting": "value"}
        boundary = "----WebKitFormBoundary12345"
        request = (
            f"POST /upload HTTP/1.1\r\n"
            f"Content-key: multipart/form-data; boundary={boundary}\r\n"
            f"\r\n"
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="file"; filename="config.json"\r\n'
            f"Content-Type: application/json\r\n"
            f"\r\n"
            f"{json.dumps(data)}\r\n"
            f"--{boundary}--\r\n"
        )

        self.server.upload_config(request)

        testConfig = RCU.import_config()

        self.assertEqual(testConfig, data)

        RCU.write_config(self.server.config)  # reset the local config


if __name__ == "__main__":
    unittest.main()
