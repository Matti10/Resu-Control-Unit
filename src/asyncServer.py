import asyncio

import tinyweb.tinyweb as tinyweb
from static import *

#init the srever
server = tinyweb.server.webserver()

@server.route("/", method="GET")
@server.route("/index.html", method="GET")
async def index(req, resp):
    print(INDEX_PATH)
    await resp.send_file(INDEX_PATH)

@server.route(f"{ROUTE_WEB_FILES}/<path>", method="GET")
async def webFiles(req,resp,path):
    print(ROUTE_WEB_FILES)
    await resp.send_file(f"{WEB_FILES_PATH}/{path}")

@server.route(ROUTE_CONFIG, method="GET")
@server.route(f"{ROUTE_CONFIG}/", method="GET")
async def getConfig(req,resp):
    print(ROUTE_CONFIG)
    await resp.send_file(CONFIG_PATH)

server.run(port=PORT,loop_forever=False)
