import asyncio

import tinyweb.tinyweb as tinyweb
from static import *


def run_method(cls,data):
    print("ee")
    return getattr(cls,data[KEY_FUNC])(*data[KEY_ARGS],**data[KEY_KWARGS])

def async_run_method(cls,data):
    return asyncio.create_task(getattr(cls,data[KEY_FUNC])(*data[KEY_ARGS],**data[KEY_KWARGS]))

def add_static_endpoints():
    @server.route("/")
    @server.route("/index.html")
    async def index(req, resp):
        await resp.send_file(INDEX_PATH)

    @server.route(f"{ROUTE_WEB_FILES}/<path>")
    async def webFiles(req,resp,path):
        await resp.send_file(f"{WEB_FILES_PATH}/{path}")

    @server.route(ROUTE_CONFIG)
    @server.route(f"{ROUTE_CONFIG}/")
    async def getConfig(req,resp):
        await resp.send_file(CONFIG_PATH)

    @server.route(ROUTE_CONFIG_UP, methods=["POST"])
    async def uploadConfig(req,resp):
        data = await req.read_parse_form_data()

#init the srever
server = tinyweb.server.webserver()
server.run(host="0.0.0.0",port=PORT,loop_forever=False)



