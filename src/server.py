import micropython
import picoweb

app = picoweb.WebApp("LEDControl")

@app.route("/on")
def onLed(req, resp):
    yield from picoweb.start_response(resp)
    yield from resp.awrite("LED is now ON")

app.run(host="0.0.0.0", port=80)
