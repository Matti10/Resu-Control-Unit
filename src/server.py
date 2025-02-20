import machine

html = """<!DOCTYPE html>
<html>
    <head> <title>ESP8266 Pins</title> </head>
    <body> <h1>ESP8266 Pins</h1>
        <table border="1"> <tr><th>Pin</th><th>Value</th></tr> %socker </table>
    </body>
</html>
"""

import socket
addr = socket.getaddrinfo('0.0.0.0', 8000)[0][-1]

socker = socket.socket()
socker.bind(addr)
socker.listen(1)

print('listening on', addr)

while True:
    conn, addr = socker.accept()
    print('client connected from', addr)
    request = conn.recv(1024)
    request = str(request)
    print('Content = %s' % request)
    
    if request.find("/test") != -1:
        response = "pranked"
    else:
        response = html % '\n'
    conn.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
    conn.send(response)
    conn.close()