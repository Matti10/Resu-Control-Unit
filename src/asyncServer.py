import json
import tinyweb.tinyweb as tinyweb
from static import *

#init the srever
server = tinyweb.server.webserver()

@server.route("/", method="GET")
@server.route("/index.html", method="GET")
async def index(req, resp):
    await resp.send_file(INDEX_PATH)

@server.route(f"{ROUTE_WEB_FILES}/<path>", method="GET")
async def webFiles(req,resp,path):
    await resp.send_file(f"{WEB_FILES_PATH}/{path}")

@server.route(ROUTE_CONFIG, method="GET")
@server.route(f"{ROUTE_CONFIG}/", method="GET")
async def getConfig(req,resp):
    print("sending cnfig")
    await resp.send_file(CONFIG_PATH)

server.run(host="192.168.0.168", port=PORT,loop_forever=False)

def run_method(cls,data):
    data = data["data"]
    return getattr(cls,data[KEY_FUNC])(*data[KEY_ARGS],**data[KEY_KWARGS])


