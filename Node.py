import requests,time,json
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib

def ask_for_data(n,key,client):
    urllib.urlencode({
        'key':key,
        'client':client
    })
    r = requests.get(n)

    if r.status_code==200:
        print("asking for data from %s success"%n)
        return r

class Server(BaseHTTPRequestHandler):
    # GET
    storage = {'1':"test_data"}
    neighbours = []
    def do_GET(s):
        print("<<==**\n Got connection:",s.path)
        #path = self.path.split('/')[1:]
        params = s.get_params()
        print(s.client_address)
        key = params['key'][0]
        data = s.storage.get(key) 
        if not data:
            # Data not found, start searching
            for n in s.neighbours:
                ask_for_data(n,key,s.client_address[0])
        else:
            s._send_resp(data)
        return

    def get_params(s):
        parsed  =urllib.parse.urlparse(s.path)
        params =urllib.parse.parse_qs(parsed.query)
        return params

    def _send_resp(self,msg,status=200):
        self.send_response(status)
        self.send_header('Content-type','text/html')
        self.end_headers()
        self.wfile.write(bytes(msg, "utf8"))


def run():
    print('starting server...')
    # Server settings
    # Choose port 8080, for port 80, which is normally used for a http server, you need root access
    port = 3880
    server_address = ('127.0.0.1',port)
    httpd = HTTPServer(server_address,Server)
    print('running server on %i...'%port)
    httpd.serve_forever()


run()

