import unittest
import testing_utils
import server

# once in production this needs to be a serperate folder that files are copied into....

REPO_ROOT = "/workspaces/Resu-Control-Unit"

class unitTestServer(unittest.TestCase):
    RCU_Server = server.RCU_server(test=True)

    def test_frontend_routes_exist(self):
        usedRoutes = testing_utils.find_endpoints_inFrontend(f"{REPO_ROOT}/src/web")

        print(f"Following routes found in UI: {usedRoutes}")

        for route in usedRoutes:
            rootRoute = "/" + route.split("/")[1]
            self.assertIn(rootRoute,self.RCU_Server.server._routes,f"{rootRoute} (from {route}) is not in server routes ({self.RCU_Server.server._routes})")


if __name__ == "__main__":
    unittest.main()