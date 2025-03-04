REPO_ROOT = "/workspaces/Resu-Control-Unit"

import os
os.chdir(f"{REPO_ROOT}/src")

import json
import unittest
import testing_utils
import server

# once in production this needs to be a serperate folder that files are copied into....


class unitTestServer(unittest.TestCase):
    def setUp(self):
        self.server = server.RCU_server(testMode=True)


    def test_frontend_routes_exist(self):
        usedRoutes = testing_utils.find_endpoints_inFrontend(f"{REPO_ROOT}/src/web")


        serverRoutes = [route["path"] for route in self.server.server._routes]

        # print(f"Following routes found in UI: {usedRoutes}")
        # print(f"Following routes found in Server: {serverRoutes}")

        for route in usedRoutes:
            rootRoute = "/" + route.split("/")[1]
            self.assertIn(rootRoute,serverRoutes,f"{rootRoute} (from {route}) is not in server routes ({self.server.server._routes})")

    # def test_hex_to_rgb_valid(self):
    #     raise Exception("This needs to be ported to a JS test")
    #     self.assertEqual(self.server.hex_to_rgb("#FF5733"), (255, 87, 51))
    #     self.assertEqual(self.server.hex_to_rgb("FF5733"), (255, 87, 51))
    
    # def test_hex_to_rgb_invalid(self):
    #     raise Exception("This needs to be ported to a JS test")

    #     with self.assertRaises(ValueError):
    #         self.server.hex_to_rgb("#FFF")
    #     with self.assertRaises(ValueError):
    #         self.server.hex_to_rgb("XYZ123")

    def test_file_exists(self):
        self.assertTrue(self.server.file_exists(__file__)) # test the file we're running exists
        self.assertFalse(self.server.file_exists("/some/garbage/path")) # test the file we're running exists


    def test_serve_file(self):
        validFiles = [__file__,server.INDEX_PATH, server.FAVICON_PATH]
        invalidFiles = ["wrong","/looks/right/but/is/wrong.lol"]

        for file in validFiles:
            result = self.server.serve_file(file)
            result = [item for item in result]

            result = b"".join(result)

            with open(file, 'rb') as file:
                content = file.read()

            self.assertEqual(content,result)

        for file in invalidFiles:
            result = self.server.serve_file(file)
            self.assertEqual("404",result)

    def test_serve_json(self):
        testObj = {
            "test" : 1,
            "test1" : "1",
            "test2" : {
                "test3" : [1,2,3]
            },
            "test4" : False
        }

        realObj = self.server.serve_json(testObj)

        print(realObj)
        print(type(realObj))

        self.assertEqual(testObj,json.loads(realObj.decode()))

if __name__ == "__main__":
    unittest.main()