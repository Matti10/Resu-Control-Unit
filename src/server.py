import os
import re
import uos
import RCU
import ujson
import micropyserver
import utils
import machine
from shiftLights import ShiftLight

WEB_FILES_ROUTE = "/webFiles"
WEB_FILES_PATH = "/workspaces/Resu-Control-Unit/src/web"
INDEX_PATH = f"{WEB_FILES_PATH}/index.html"
FAVICON_ROUTE = "/favicon.ico"
FAVICON_PATH = f"{WEB_FILES_PATH}/resu-horiz-white.png"

PORT = 8000

class RCU_server:
    
    def __init__(self,config=None):
        
        
        if None == config:
            self.config = RCU.import_config() # dont duplicate config
        else:
            self.config = config    
        
        self.shiftLights = ShiftLight(self.config)

        self.server = micropyserver.MicroPyServer(port=PORT)
        self.server.add_route("/", self.get_webFiles)
        self.server.add_route("/shiftLights", self.get_shiftLights)
        self.server.add_route("/shiftLights", self.post_shiftLight,method="POST")
        self.server.add_route("/pins", self.get_pins)
        self.server.add_route(WEB_FILES_ROUTE, self.get_webFiles)
        self.server.add_route(FAVICON_ROUTE, self.get_favicon)
        self.server.add_route("/downloadConfig", self.download_config)
        self.server.add_route("/uploadConfig", self.upload_config, method="POST")
            
        self.server._print_routes()
        self.server.start()
    
    # Utils

    def post_saveConfig(self,request):
        try:
            RCU.export_config(self.config)
            utils.send_response(self.server, "Config Saved", http_code=201)
        except:
            utils.send_response(self.server, f"Error saving config with request:\n{request}", http_code=500)
    
    def hex_to_rgb(self,hex_color):
        # Remove '#' if present
        hex_color = hex_color.lstrip('#')
        
        # Convert hex to RGB
        if len(hex_color) == 6:  # Standard format (e.g., "FF5733")
            r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
            return r, g, b
        else:
            raise ValueError("Invalid hex color format. Use #RRGGBB.")

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
        print(f"serving:{path}")
        self.server.send(f"HTTP/1.1 200 OK\r\nContent-Type: {utils.get_content_type(path)}\r\n\r\n")
        with open(path, "rb") as f:  # Open file in binary mode
            while chunk := f.read(512):  # Read in chunks (512 bytes)
                self.server.send_bytes(chunk)  # Send each chunk

    def serve_json(self,data):      
        utils.send_response(self.server,ujson.dumps(data),content_type="application/json")

    # Shift Lights
    def post_shiftLight(self,request):
        _,path,body = utils.parse_request(request)
        message = f"endpoint not found for {path}" # this will get overwritten
        
        if "" != body:
            data = ujson.loads(body)
            print(f"data:{data}")
            
        if re.match(r"/shiftLights/\d+", path):  
            id = int(re.search(r"\d+", path).group(0))  # Extracts the ID
            message = f"Set light color @ index {id}"
            self.shiftLights.set_configed_color(id,self.hex_to_rgb(data.get("color")))
        elif re.match(r"/shiftLights/LimiterColor", path):
            message = "setting limiter color"
            self.shiftLights.set_configed_limiter_color(self.hex_to_rgb(data.get("color")))

        elif re.match(r"/shiftLights/limitPattern", path):
            message = "setting limiter pattern"
            self.shiftLights.set_limiter_pattern(data.get("pattern"))
        elif re.match(r"/shiftLights/pin", path):
            message = f"setting shift light pin to {data.get("selectedPin")}"
            self.shiftLights.set_pin(data.get("selectedPin"))
        else:
            #return 404
            self.server._route_not_found(request)
            return

        print(message)
        utils.send_response(self.server, message, http_code=201)
        
        # save changes
        RCU.export_config(self.config)

    

    def get_shiftLights(self,_):
        self.serve_json(self.shiftLights.get_shiftLights())

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
            print(f"Error serving file: {e}")
            self.server.send("HTTP/1.1 500 Internal Server Error\r\n")
            self.server.send("Content-Type: text/plain\r\n")
            self.server.send("\r\n")
            self.server.send("Error serving file")
    
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
            print(f"Error uploading file: {e}")
            self.server.send("HTTP/1.1 500 Internal Server Error\r\n")
            self.server.send("Content-Type: text/plain\r\n")
            self.server.send("\r\n")
            self.server.send("Error uploading file")
    
RCU_server()