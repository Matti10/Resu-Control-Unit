# import micropython
import picoweb

app = picoweb.WebApp("LEDControl")

@app.route("/")
def onLed(req, resp):
    yield from picoweb.start_response(resp)
    with open("web\index.html", "r") as f:
        yield from resp.awrite(f.read())

app.run(host="0.0.0.0", port=80)
