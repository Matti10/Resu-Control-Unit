import re

try:
    import uos as os
except:
    import os

try:
    import ujson as json
except:
    import json

import micropyserver
import RCU
import utils
from static import *

ROUTE_WEB_FILES = "/webFiles"
WEB_FILES_PATH = "/workspaces/Resu-Control-Unit/src/web"
INDEX_PATH = f"{WEB_FILES_PATH}/index.html"
ROUTE_FAVICON = "/favicon.ico"
FAVICON_PATH = f"{WEB_FILES_PATH}/resu-horiz-white.png"
PORT = 8000

ROUTE_CONFIG = "/config"
ROUTE_RPM = "/rpm"
ROUTE_ADDFUNC = "/addFunc"
ROUTE_RMFUNC = "/rmFunc"
KEY_STRING_JSON = "json"
KEY_STRING_INT = "int"
KEY_STRING_STRING = "string"


class RouteNotFound(Exception):
    def __init__(self, message, server):
        # Initialize the exception with a message
        super().__init__(message)
        # return 404
        server._route_not_found(message)


class InternalError(Exception):
    def __init__(self, server, message="Internal Server Error"):
        # Initialize the exception with a message
        super().__init__(message)
        # return 404
        server._internal_error(message)


class RCU_server:
    def __init__(self, RCU, testMode=False):
        self.testMode = testMode
        self.RCU = RCU

        self.server = micropyserver.MicroPyServer(port=PORT, testMode=testMode)
        self.server.add_route("/", self.get_webFiles)
        self.server.add_route("/ShiftLights", self.post_shiftLight, method="POST")
        self.server.add_route(ROUTE_WEB_FILES, self.get_webFiles)
        self.server.add_route(ROUTE_FAVICON, self.get_favicon)
        self.server.add_route("/downloadConfig", self.download_config)
        self.server.add_route("/uploadConfig", self.upload_config, method="POST")
        self.server.add_route(ROUTE_CONFIG, self.set_config, method="POST")
        self.server.add_route(ROUTE_ADDFUNC, self.add_rcuFunc, method="POST")
        self.server.add_route(ROUTE_RMFUNC, self.rm_rcuFunc, method="POST")
        self.server.add_route(ROUTE_CONFIG, self.get_config)
        self.server.add_route(ROUTE_RPM, self.get_rpm)
        self.server._print_routes()


        if not testMode:
            self.server.start()
    
    def add_rcuFunc(self,request,preParsedRequest=None):
        _, path, body, _ = utils.handle_preparsed_request(request, preParsedRequest)
                # process the data
        body = json.loads(body)
        key = next(iter(body))

        data = body[key]

        rcuFunc = self.RCU.add_RCUFunc(data)
        self.RCU.export_config()
        utils.send_response(self.server, rcuFunc.functionID, http_code=201)


    def rm_rcuFunc(self, request, preParsedRequest=None):
        _, _, body, _ = utils.handle_preparsed_request(request, preParsedRequest)
        
        body = json.loads(body)
        funcID = body["data"]
        self.RCU.remove_RCUFunc(funcID)
        self.RCU.export_config()
        utils.send_response(self.server, "", http_code=201)



    def get_config(self, request, preParsedRequest=None):
        _, path, _, _ = utils.handle_preparsed_request(request, preParsedRequest)
        print(f"keys:{utils.get_config_keys(path, ROUTE_CONFIG)}")
        return self.serve_file(CONFIG_PATH)

    def set_config(self, request, preParsedRequest=None):
        _, path, body, _ = utils.handle_preparsed_request(request, preParsedRequest)
        print(path)
        # process the data
        body = json.loads(body)
        key = next(iter(body))

        data = body[key]

        print(f"found data under '{key}' with value {data}")

        keys = utils.get_config_keys(path, ROUTE_CONFIG)

        try:
            utils.set_nested_dict(self.config, keys, data)
        except Exception as e:
            print(e)
            raise RouteNotFound(path, self.server)

        # save changes
        if not self.testMode:
            RCU.RCU.write_config(self.config)

        utils.send_response(self.server, "", http_code=201)

    def file_exists(self, path):
        try:
            os.stat(path)  # Check file stats
            return True  # File exists
        except OSError:  # File not found or inaccessible
            return False

    def get_favicon(self, _):
        self.serve_file(FAVICON_PATH)

    def get_webFiles(self, request):
        _, path, _, _ = utils.parse_request(request)
        path = path.replace(ROUTE_WEB_FILES, WEB_FILES_PATH)
        print(f"path:{path}")
        if path == "/":
            path = INDEX_PATH

        if self.file_exists(path):
            return self.serve_file(path)
        else:
            raise RouteNotFound(path, self.server)

    def serve_file(self, path):
        result = []  # used for tests becasue no mocking in micropy
        print(f"serving:{path}")
        try:
            self.server.send(
                f"HTTP/1.1 200 OK\r\nContent-key: {utils.get_content_type(path)}\r\n\r\n"
            )
            with open(path, "rb") as f:  # Open file in binary mode
                while chunk := f.read(512):  # Read in chunks (512 bytes)
                    # Send each chunk
                    result.append(self.server.send_bytes(chunk))
            if self.testMode:
                return result
        except OSError as e:
            raise RouteNotFound(path, self.server)  # send a 404

    def serve_json(self, data):
        return utils.send_response(
            self.server, json.dumps(data), content_type="application/json"
        )  # returning for tests

    # seperate endpoint for Shift Lights so config changes can be updated on physical lights
    def post_shiftLight(self, request):
        def sample_color(settingArea="lib_shiftLights"):
            # display changes on lib_shiftlights
            print(self.config["lib_shiftLights"]["lib_shiftLights"]["colors"])
            self.RCU.INSTACE_REGISTER[SHIFTLIGHT_TYPE].setAll_color_fromConfig(settingArea)
            self.RCU.INSTACE_REGISTER[SHIFTLIGHT_TYPE].update()

        _, path, body, _ = utils.parse_request(request)

        # Check if the path matches the main color setting route
        colorRouteMatch = re.match(
            r"/lib_shiftLights/(lib_shiftLights|Limiter)/colors/\[(\d+)\]/color", path
        )
        if colorRouteMatch:
            # Extracts 'lib_shiftLights' or 'LimiterColor'
            settingArea = colorRouteMatch.group(1)
            # update config
            self.set_config(request, preParsedRequest=(_, path, body, _))
            sample_color(settingArea)
            return

        patternRouteMatch = re.match(
            r"/lib_shiftLights/(lib_shiftLights|Limiter)/pattern/selected", path
        )
        # Check if the path matches the second pattern (limit pattern)
        if patternRouteMatch:
            settingArea = patternRouteMatch.group(1)
            # update config
            self.set_config(request, preParsedRequest=(_, path, body, _))
            self.lib_shiftLights.sample_pattern(settingArea)
            return

        brightnessRouteMatch = re.match(r"/lib_shiftLights/brightness", path)
        if brightnessRouteMatch:
            # update config
            self.set_config(request, preParsedRequest=(_, path, body, _))
            sample_color()
            return

        # If no match found, raise RouteNotFound
        raise RouteNotFound(path, self.server)

    def download_config(self, _):
        self.download_file(RCU.RCU.get_rawConfig(), "RCU-Config.json")

    def download_file(self, file_content, downloadName):
        try:
            self.server.send("HTTP/1.1 200 OK\r\n")
            self.server.send("Content-key: application/json\r\n")
            self.server.send(
                f'Content-Disposition: attachment; filename="{downloadName}"\r\n'
            )
            self.server.send("Content-Length: {}\r\n".format(len(file_content)))
            self.server.send("\r\n")
            return self.server.send_bytes(file_content)
        except OSError as e:
            raise InternalError(server=self.server, message=str(e))


    def upload_config(self, request):
        try:
            _, _, body, headers = utils.parse_request(request)
            print(f"headers:\n{headers}")

            # Extract boundary from Content-Type header
            content_type_line = [
                line for line in headers.split("\r\n") if "Content-Type: multipart/form-data" in line
            ][0]
            boundary = content_type_line.split("boundary=")[1]

            # Split the body by the boundary marker
            parts = body.split(f"--{boundary}")

            for part in parts:
                if "Content-Disposition" in part and 'name="file"' in part:
                    # Separate headers from content
                    header_and_content = part.split("\r\n\r\n", 1)
                    if len(header_and_content) != 2:
                        continue  # skip malformed parts

                    headers_block, file_content = header_and_content

                    # The file content ends just before the next boundary, but may have a trailing \r\n
                    # We remove only one trailing \r\n if present, NOT all of them
                    if file_content.endswith("\r\n"):
                        file_content = file_content[:-2]

                    # Save the file
                    with open(CONFIG_PATH, "wb") as f:
                        f.write(file_content.encode("utf-8"))
                    print(f"Saved config file, size: {len(file_content)} bytes")
                    break  # Done with file

            # Send response
            self.server.send("HTTP/1.1 200 OK\r\n")
            self.server.send("Content-Type: application/json\r\n")
            self.server.send("\r\n")
            self.server.send(json.dumps({"message": "File uploaded successfully"}))

            if not self.testMode:
                self.config = RCU.RCU.import_config(CONFIG_PATH)

        except Exception as e:
            raise InternalError(
                server=self.server, message=f"Error uploading file: {e}"
            )
        
    def get_rpm(self,_):
        try:
            rpm = str(self.lib_rpmReader.get_rpm())
        except Exception:
            rpm = "No RPM"
        self.serve_json({"rpm": rpm})
        



if __name__ == "__main__":
    import testing_utils
    config = RCU.RCU.import_config()
    # shift = ShiftLight(config=config,neoPixel=testing_utils.MockedNeoPixel,pin=testing_utils.MockedPin)
    RCU_server(None, False, config=config)
