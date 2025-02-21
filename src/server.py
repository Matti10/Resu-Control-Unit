try: 
    import usocket as socket
except:
    import socket
import re
import uos
import RCU
import ujson

INDEX_PATH = "/workspaces/Resu-Control-Unit/src/web/index.html"

def hex_to_rgb(hex_color):
    # Remove '#' if present
    hex_color = hex_color.lstrip('#')
    
    # Convert hex to RGB
    if len(hex_color) == 6:  # Standard format (e.g., "FF5733")
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        return r, g, b
    else:
        raise ValueError("Invalid hex color format. Use #RRGGBB.")

def get_content_type(path):
    """Return the correct Content-Type based on the file extension."""
    if path.endswith(".html"):
        return "text/html"
    elif path.endswith(".css"):
        return "text/css"
    elif path.endswith(".js"):
        return "application/javascript"
    elif path.endswith(".png"):
        return "image/png"
    elif path.endswith(".jpg") or path.endswith(".jpeg"):
        return "image/jpeg"
    elif path.endswith(".ico"):
        return "image/x-icon"
    else:
        return "text/plain"
    
def process_request(request):
    # Extract the method and path using regex
    match = re.search(r"^(GET|POST|PUT|DELETE|PATCH|OPTIONS|HEAD) (\S+)", request)
    
    # Split request into headers and body using "\r\n\r\n" (standard HTTP separator)
    parts = request.split("\r\n\r\n", 1)  
    body = parts[1] if len(parts) > 1 else ""  # Extract body if it exists

    if match:
        return match.group(1), match.group(2), body  # Return method, path, and body
    else:
        return "No Match", "No Match", ""

def file_exists(path):
    try:
        uos.stat(path)  # Check file stats
        return True         # File exists
    except OSError:         # File not found or inaccessible
        return False
    
def serve_404(conn,info):
    print()
    conn.send(f"HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\n\r\nPage not found\n\n{info}")
    conn.close()

def serve_file(conn, path=INDEX_PATH):
    if file_exists(path):
        conn.send(f"HTTP/1.1 200 OK\r\nContent-Type: {get_content_type(path)}\r\n\r\n")
        with open(path, "rb") as f:  # Open file in binary mode
            while chunk := f.read(512):  # Read in chunks (512 bytes)
                conn.send(chunk)  # Send each chunk
    else:
        serve_404(conn,path)

def serve_json(con,data):
    conn.send("HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n" + ujson.dumps(data))

def handle_shiftLight(path,body):
    data = ujson.loads(body)
    print(f"data:{data}")
    if re.match(r"/shiftLights/\d+", path):  
        id = int(re.search(r"\d+", path).group(0))  # Extracts the ID
        print(f"setting light color @ index {id}")

        red,green,blue = hex_to_rgb(data.get("color"))

        config["ShiftLights"]["ShiftLights"][id]["color"]["red"] = red
        config["ShiftLights"]["ShiftLights"][id]["color"]["green"] = green
        config["ShiftLights"]["ShiftLights"][id]["color"]["blue"] = blue

        print(config["ShiftLights"]["ShiftLights"][id])

    elif re.match(r"/shiftLights/limitColor", path):
        print("setting limiter color")
    elif re.match(r"/shiftLights/limitPattern", path):
        print("setting limiter pattern")
        

config = RCU.import_config()

addr = socket.getaddrinfo('0.0.0.0', 8000)[0][-1]

s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
s.listen(1)

print('listening on', addr)

while True:
    conn, addr = s.accept()
    print('client connected from', str(addr))
    request = conn.recv(1024).decode()
    print('Content = %s' % request)
    
    method,path,body = process_request(request)

    print(f"method:{method}")
    print(f"path:{path}")
    print(f"body:{body}")

    if path == "/":
        serve_file(conn,INDEX_PATH)
    elif "/shiftLights" in path:
        if method == "GET":
            serve_json(conn,config["ShiftLights"])
        elif method == "POST":
            handle_shiftLight(path,body)


    elif method == "GET":
        serve_file(conn,path)

    conn.close()