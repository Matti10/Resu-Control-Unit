import re
import uos
import RCU
import ujson
import micropyserver
import utils
from shiftLights import ShiftLight

WEB_FILES_ROUTE = "/webFiles"
WEB_FILES_PATH = "/src/web"
INDEX_PATH = f"{WEB_FILES_PATH}/index.html"
FAVICON_ROUTE = "/favicon.ico"
FAVICON_PATH = f"{WEB_FILES_PATH}/resu-horiz-white.png"
PORT = 8000

class RouteNotFound(Exception):
    def __init__(self, message):
        # Initialize the exception with a message
        super().__init__(message)
        self.message = message

class RCU_server:
    
    def __init__(self,config=None,testMode=False):
        if None == config:
            self.config = RCU.import_config() # dont duplicate config
        else:
            self.config = config

        self.testMode = testMode
        
        
        self.shiftLights = ShiftLight(self.config,testMode=True)

        self.server = micropyserver.MicroPyServer(port=PORT,testMode=testMode)
        self.server.add_route("/", self.get_webFiles)
        self.server.add_route("/shiftLights", self.get_shiftLights)
        self.server.add_route("/shiftLights", self.post_shiftLight,method="POST")
        self.server.add_route("/pins", self.get_pins)
        self.server.add_route(WEB_FILES_ROUTE, self.get_webFiles)
        self.server.add_route(FAVICON_ROUTE, self.get_favicon)
        self.server.add_route("/downloadConfig", self.download_config)
        self.server.add_route("/uploadConfig", self.upload_config, method="POST")
        self.server._print_routes()
        
        if not testMode:
            self.server.start()
    
    # Utils
    def post_saveConfig(self,request):
        try:
            RCU.export_config(self.config)
            utils.send_response(self.server, "Config Saved", http_code=201)
        except Exception as e:
            self.server_internalError(f"Error saving config with request:\n{request}\n Error:{e}")
    

    def file_exists(self,path):
        try:
            uos.stat(path)  # Check file stats
            return True         # File exists
        except OSError:         # File not found or inaccessible
            return False

    def get_favicon(self,_):
        self.serve_file(FAVICON_PATH)
        

    def get_webFiles(self,request):
        _,path,_ = utils.parse_request(request)
        path = path.replace(WEB_FILES_ROUTE,WEB_FILES_PATH)
        print(f"path:{path}")
        if path == "/":
            path = INDEX_PATH
            
        if self.file_exists(path):
            self.serve_file(path)
        else:
            self.server._route_not_found(request)

    def serve_file(self,path):
        result = [] #used for tests becasue no mocking in micropy
        print(f"serving:{path}")
        try:
            self.server.send(f"HTTP/1.1 200 OK\r\nContent-Type: {utils.get_content_type(path)}\r\n\r\n")
            with open(path, "rb") as f:  # Open file in binary mode
                while chunk := f.read(512):  # Read in chunks (512 bytes)
                    result.append(self.server.send_bytes(chunk))  # Send each chunk
            if self.testMode:
                return result
        except OSError as e:
            return self.server._route_not_found(path) #send a 404


    def serve_json(self,data):
        return utils.send_response(self.server,ujson.dumps(data),content_type="application/json") # returning for tests

    # Shift Lights
    def post_shiftLight(self,request):
        _,path,body = utils.parse_request(request)
        message = f"endpoint not found for {path}" # this will get overwritten

        try:
            if "" != body:
                data = ujson.loads(body)
                print(f"data:{data}")

            # Check if the path matches the main color setting route
            colorRouteMatch = re.match(r"/shiftLights/(shiftLights|LimiterColor)/(\d+)", path)

            if colorRouteMatch:
                settingArea = colorRouteMatch.group(1)  # Extracts 'shiftLights' or 'LimiterColor'
                id = int(colorRouteMatch.group(2))  # Extracts the ID as an integer

                message = f"Set light color for {settingArea} @ index {id}"
                self.shiftLights.set_configed_color(id, data.get("color"), subKey=settingArea, update=True)

            # Check if the path matches the second pattern (limit pattern)
            elif re.match(r"/shiftLights/limitPattern", path):
                message = "setting limiter pattern"
                self.shiftLights.set_limiter_pattern(data.get("pattern"))

            # Check if the path matches the third pattern (shift light pin)
            elif re.match(r"/shiftLights/pin", path):
                message = f"setting shift light pin to {data.get('selectedPin')}"
                self.shiftLights.set_pin(data.get("selectedPin"))

            # If no match found, raise RouteNotFound
            else:
                raise RouteNotFound(path)

            utils.send_response(self.server, message, http_code=201)
        except RouteNotFound as e:
            #return 404
            self.server._route_not_found(e)
        finally:
            print(message)

        # save changes
        RCU.export_config(self.config)

    def server_internalError(self,message="Internal Server Error"):
        print(message)
        self.server.send("HTTP/1.1 500 Internal Server Error\r\n")
        self.server.send("Content-Type: text/plain\r\n")
        self.server.send("\r\n")
        self.server.send("Error uploading file")

    def get_shiftLights(self,_):
        self.serve_json(self.shiftLights.get_shiftLightConfig())

    # Pins 
    def get_pins(self, _):
        self.serve_json(self.config["Pins"])
        
    def download_config(self,_):
        self.download_file(RCU.get_rawConfig())
        
    def download_file(self,file_content):
        try:
            self.server.send("HTTP/1.1 200 OK\r\n")
            self.server.send("Content-Type: application/json\r\n")
            self.server.send(f"Content-Disposition: attachment; filename=\"config.json\"\r\n")
            self.server.send("Content-Length: {}\r\n".format(len(file_content)))
            self.server.send("\r\n")
            self.server.send_bytes(file_content)
        except OSError as e:
            self.server_internalError(f"Error serving file: {e}")
    
    def upload_config(self, request):
        try:
            headers, _, body = utils.parse_request(request)
            content_type_header = [header for header in headers.split('\r\n') if 'Content-Type' in header][0]
            boundary = content_type_header.split('=')[1]
            parts = body.split(f'--{boundary}')
            
            for part in parts:
                if 'Content-Disposition' in part:
                    headers, file_content = part.split('\r\n\r\n', 1)
                    file_content = file_content.rsplit('\r\n', 1)[0]
                    with open(RCU.CONFIG_PATH, 'wb') as f:
                        f.write(file_content.encode('utf-8'))
                    break
            
            self.server.send("HTTP/1.1 200 OK\r\n")
            self.server.send("Content-Type: application/json\r\n")
            self.server.send("\r\n")
            self.server.send(ujson.dumps({"message": "File uploaded successfully"}))
            
            self.config = RCU.import_config(RCU.CONFIG_PATH)
        except Exception as e:
            self.server_internalError(f"Error uploading file: {e}")
            
if __name__ == "__main__":
    RCU_server(None,False)