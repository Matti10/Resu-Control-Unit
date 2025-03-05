import re

import ujson
import uos

import micropyserver
import RCU
import utils
from shiftLights import ShiftLight

ROUTE_WEB_FILES = "/webFiles"
WEB_FILES_PATH = "/web"
INDEX_PATH = f"{WEB_FILES_PATH}/index.html"
ROUTE_FAVICON = "/favicon.ico"
FAVICON_PATH = f"{WEB_FILES_PATH}/resu-horiz-white.png"
PORT = 8000

ROUTE_CONFIG = "/config"

key_STRING_JSON = "json"
key_STRING_INT = "int"
key_STRING_STRING = "string"


class RouteNotFound(Exception):
    def __init__(self, message, server):
        # Initialize the exception with a message
        super().__init__(message)
        self.message = message
        # return 404
        server._route_not_found(message)


class RCU_server:
    def __init__(self, config=None, testMode=False):
        if None == config:
            self.config = RCU.import_config()  # dont duplicate config
        else:
            self.config = config

        self.testMode = testMode

        self.ShiftLights = ShiftLight(self.config, testMode=True)

        self.server = micropyserver.MicroPyServer(port=PORT, testMode=testMode)
        self.server.add_route("/", self.get_webFiles)
        self.server.add_route("/ShiftLights", self.post_shiftLight, method="POST")
        self.server.add_route(ROUTE_WEB_FILES, self.get_webFiles)
        self.server.add_route(ROUTE_FAVICON, self.get_favicon)
        self.server.add_route("/downloadConfig", self.download_config)
        self.server.add_route("/uploadConfig", self.upload_config, method="POST")
        self.server.add_route(ROUTE_CONFIG, self.set_config, method="POST")
        self.server.add_route(ROUTE_CONFIG, self.get_config)
        self.server._print_routes()

        if not testMode:
            self.server.start()

    # Utils
    def post_saveConfig(self, request):
        try:
            RCU.export_config(self.config)
            utils.send_response(self.server, "Config Saved", http_code=201)
        except Exception as e:
            self.server_internalError(
                f"Error saving config with request:\n{request}\n Error:{e}"
            )

    def get_config_keys(self, path):
        # strip the leading / and then the "config". doing this in two steps allows for passing of paths that dont have the leading "/config"
        keys = path.strip("/").strip(ROUTE_CONFIG[1:]).split("/")
        keys = [key for key in keys if key != ""]  # remove blank strings

        return keys

    def get_config(self, request, preParsedRequest=None):
        _, path, _ = utils.handle_preparsed_request(request, preParsedRequest)

        self.serve_json(utils.get_nested_dict(self.config, self.get_config_keys(path)))
        utils.send_response(self.server, "", http_code=201)

    def set_config(self, request, preParsedRequest=None):
        _, path, body = utils.handle_preparsed_request(request, preParsedRequest)

        # process the data
        body = ujson.loads(body)
        key = next(iter(body))

        data = body[key]

        print(f"found data under '{key}' with value {data}")

        keys = self.get_config_keys(path)

        if utils.get_nested_dict(
            self.config, keys
        ):  # TODO decide if this search is neccesary, alot of looping for no reeeeeal reason
            utils.set_nested_dict(self.config, keys, data)
        else:
            raise RouteNotFound(path, self.server)

        # save changes
        RCU.export_config(self.config)

        utils.send_response(self.server, "", http_code=201)

    def file_exists(self, path):
        try:
            uos.stat(path)  # Check file stats
            return True  # File exists
        except OSError:  # File not found or inaccessible
            return False

    def get_favicon(self, _):
        self.serve_file(FAVICON_PATH)

    def get_webFiles(self, request):
        _, path, _ = utils.parse_request(request)
        path = path.replace(ROUTE_WEB_FILES, WEB_FILES_PATH)
        print(f"path:{path}")
        if path == "/":
            path = INDEX_PATH

        if self.file_exists(path):
            self.serve_file(path)
        else:
            self.server._route_not_found(request)

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
            return self.server._route_not_found(path)  # send a 404

    def serve_json(self, data):
        return utils.send_response(
            self.server, ujson.dumps(data), content_type="application/json"
        )  # returning for tests

    # seperate endpoint for Shift Lights so config changes can be updated on physical lights
    def post_shiftLight(self, request):
        _, path, body = utils.parse_request(request)
        message = f"endpoint not found for {path}"  # this will get overwritten
        print(path, body)
        try:
            # Check if the path matches the main color setting route
            colorRouteMatch = re.match(
                r"/ShiftLights/(ShiftLights|LimiterColor)/(\d+)", path
            )
            if colorRouteMatch:
                # Extracts 'ShiftLights' or 'LimiterColor'
                settingArea = colorRouteMatch.group(1)
                # Extracts the ID as an integer
                id = int(colorRouteMatch.group(2))

                message = f"Set light color for {settingArea} @ index {id}"

                # update config
                self.set_config(request, preParsedRequest=(_, path, body))

                # display changes on shiftlights
                self.ShiftLights.setAll_color_fromConfig(settingArea)
                self.ShiftLights.update()

            # Check if the path matches the second pattern (limit pattern)
            elif re.match(r"/ShiftLights/limitPattern", path):
                message = "setting limiter pattern"

                # update config
                self.set_config(request, preParsedRequest=(_, path, body))
                self.ShiftLights.sample_limiter()

            # If no match found, raise RouteNotFound
            else:
                raise RouteNotFound(path, self.server)

        except RouteNotFound:
            pass  # breakout of above logic
        finally:
            print(message)

    def server_internalError(self, message="Internal Server Error"):
        print(message)
        self.server.send("HTTP/1.1 500 Internal Server Error\r\n")
        self.server.send("Content-key: text/plain\r\n")
        self.server.send("\r\n")
        self.server.send("Error uploading file")

    def download_config(self, _):
        self.download_file(RCU.get_rawConfig())

    def download_file(self, file_content):
        try:
            self.server.send("HTTP/1.1 200 OK\r\n")
            self.server.send("Content-key: application/json\r\n")
            self.server.send(
                f'Content-Disposition: attachment; filename="config.json"\r\n'
            )
            self.server.send("Content-Length: {}\r\n".format(len(file_content)))
            self.server.send("\r\n")
            self.server.send_bytes(file_content)
        except OSError as e:
            self.server_internalError(f"Error serving file: {e}")

    def upload_config(self, request):
        try:
            headers, _, body = utils.parse_request(request)
            content_type_header = [
                header for header in headers.split("\r\n") if "Content-key" in header
            ][0]
            boundary = content_type_header.split("=")[1]
            parts = body.split(f"--{boundary}")

            for part in parts:
                if "Content-Disposition" in part:
                    headers, file_content = part.split("\r\n\r\n", 1)
                    file_content = file_content.rsplit("\r\n", 1)[0]
                    with open(RCU.CONFIG_PATH, "wb") as f:
                        f.write(file_content.encode("utf-8"))
                    break

            self.server.send("HTTP/1.1 200 OK\r\n")
            self.server.send("Content-key: application/json\r\n")
            self.server.send("\r\n")
            self.server.send(ujson.dumps({"message": "File uploaded successfully"}))

            self.config = RCU.import_config(RCU.CONFIG_PATH)
        except Exception as e:
            self.server_internalError(f"Error uploading file: {e}")


if __name__ == "__main__":
    RCU_server(None, False)
