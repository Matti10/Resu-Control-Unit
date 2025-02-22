import os
import re
import uos
import RCU
import ujson
import micropyserver
import utils

WEB_FILES_ROUTE = "/webFiles"
WEB_FILES_PATH = "/workspaces/Resu-Control-Unit/src/web"
INDEX_PATH = f"{WEB_FILES_PATH}/index.html"

PORT = 8000

class RCU_server:
    
    def __init__(self,config=None):
        
        if None == config:
            self.config = RCU.import_config() # dont duplicate config
        else:
            self.config = config    

        self.server = micropyserver.MicroPyServer(port=PORT)
        self.server.add_route("/", self.get_webFiles)
        self.server.add_route("/shiftLights", self.get_shiftLights)
        self.server.add_route("/shiftLights", self.post_shiftLight,method="POST")
        self.server.add_route(WEB_FILES_ROUTE, self.get_webFiles)
        self.server.add_route("/save", self.get_webFiles,method="POST")
            
        self.server._print_routes()
        self.server.start()
    
    def set_light_config_color(self,lightsConfig,hex_color):
        red,green,blue = self.hex_to_rgb(hex_color)
        
        lightsConfig["color"]["red"] = red
        lightsConfig["color"]["green"] = green
        lightsConfig["color"]["blue"] = blue
    
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
        
    def get_webFiles(self,request):
        _,path,_ = utils.parse_request(request)
        path = path.replace(WEB_FILES_ROUTE,WEB_FILES_PATH)
        print(f"path:{path}")
        if path == "/":
            path = INDEX_PATH
        if self.file_exists(path):
            self.server.send(f"HTTP/1.1 200 OK\r\nContent-Type: {utils.get_content_type(path)}\r\n\r\n")
            
            self.serve_file(path)
        else:
            self.server._route_not_found(request)

    def serve_file(self,path):
        print(f"serving:{path}")
        
        with open(path, "rb") as f:  # Open file in binary mode
            while chunk := f.read(512):  # Read in chunks (512 bytes)
                self.server.send_bytes(chunk)  # Send each chunk


    def serve_json(self,data):      
        utils.send_response(self.server,ujson.dumps(data),content_type="application/json")

    def post_shiftLight(self,request):
        _,path,body = utils.parse_request(request)
        if "" != body:
            data = ujson.loads(body)
            print(f"data:{data}")
            
        if re.match(r"/shiftLights/\d+", path):  
            id = int(re.search(r"\d+", path).group(0))  # Extracts the ID
            message = f"Set light color @ index {id}"
            print(message)

            self.set_light_config_color(self.config["ShiftLights"]["ShiftLights"][id],data.get("color"))

            print(self.config["ShiftLights"]["ShiftLights"][id])
            
        elif re.match(r"/shiftLights/LimiterColor", path):
            message = "setting limiter color"
            print(message)
            
            self.set_light_config_color(self.config["ShiftLights"]["LimiterColor"],data.get("color"))

        elif re.match(r"/shiftLights/limitPattern", path):
            message = "setting limiter pattern"
            print(message)
        else:
            #return 404
            self.server._route_not_found(request)
            return

        utils.send_response(self.server, message, http_code=201)
        

    def get_shiftLights(self,request):
        self.serve_json(self.config["ShiftLights"])
        
    def post_saveConfig(self,request):
        try:
            RCU.export_config(self.config)
            utils.send_response(self.server, "Config Saved", http_code=201)
        except:
            utils.send_response(self.server, f"Error saving config with request:\n{request}", http_code=500)
            
    def test(self,request):
        print(request)
        utils.send_response(self.server,"<h1> test</h1>")

RCU_server()
    # self.server.add_route("/another_action", another_action)
    # ''' start self.server '''
    # print('listening on', addr)

    # while True:
    #     self.server, addr = s.accept()
    #     print('client connected from', str(addr))
    #     request = self.server.recv(1024).decode()
    #     print('Content = %s' % request)
        
        # method,path,body = parse_request(request)

    #     print(f"method:{method}")
    #     print(f"path:{path}")
    #     print(f"body:{body}")

    #     if path == "/":
    #         serve_file(INDEX_PATH)
    #     elif "/shiftLights" in path:
    #         if method == "GET":
    #             serve_json(config["ShiftLights"])
    #         elif method == "POST":
    #             handle_shiftLight(path,body)


    #     elif method == "GET":
    #         serve_file(path)

    #     self.server.close()