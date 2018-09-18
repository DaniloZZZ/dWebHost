import requests,time,json
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib
import argparse
parser = argparse.ArgumentParser(
    description='run node')
parser.add_argument('port',
                    help='port to run')
parser.add_argument('add_key',
                    help='new cuskey')
args = parser.parse_args()

def ask_for_data(n,key,client):
    params = urllib.parse.urlencode({
        'key':key,
        'client':client
    })
    r = requests.get('http://'+n+'?'+params)

    if r.status_code==200:
        print("asking for data from %s success"%n)
        return r.text
    else:
        print(r.status_code)
        print(r,n)
SELF = ''

class Server(BaseHTTPRequestHandler):
    # GET
    storage = {'1':"test_data",args.add_key:'CUSTOM'+args.add_key}
    neighbours = ['127.0.0.1:3880']
    def do_GET(s):
        print("<<==**\n Got connection:",s.path)
        params = s.get_params()
        print('params of conn',s.client_address,params)
        key = params['key'][0]
        if key =='nodes_':
            data = json.dumps(s.neighbours)
            s._send_resp(data)
            return
        client = params.get('client')
        #direct = False
        if not client:
            client = s.client_address[0]
        else:
            #client = client[0]
            nadr =client
            if nadr not in s.neighbours:
                print('appending neighbour',nadr)
                s.neighbours+=nadr
            #direct = True
        data = s.storage.get(key) 
        print("data",data)
        if not data:
            # Data not found, start searching
            for n in s.neighbours:
                if n!=SELF and n!=client:
                    # do not ask the client itself
                    data = ask_for_data(n,key,SELF)
                    print("got data from",n,data)
                    s._send_resp(data)
                    return
            s._send_resp('NOTHING')
            return
        else:
            # todo: send directly to client
            print("sending my data back")
            s._send_resp(data)
            return

        for n in s.neighbours:
            neigh = s.get_neigh(n)
        if neigh:
            s.neighbours.append(neigh)
        return

    def get_params(s):
        parsed  =urllib.parse.urlparse(s.path)
        params =urllib.parse.parse_qs(parsed.query)
        return params

    def get_neigh(s,node):
        global SELF
        if SELF==node:
            return
        text = ask_for_data(node,'nodes_',SELF)
        print('got nodes from',node,text)
        ns = json.loads(text)
        print(ns)
        return ns

    def _send_resp(self,msg,status=200):
        self.send_response(status)
        self.send_header('Content-type','text/html')
        self.end_headers()
        self.wfile.write(bytes(msg, "utf8"))

def run():
    global SELF

    print('starting server...')
    # Server settings
    port =  int(args.port) or 3880
    SELF = '127.0.0.1:'+str(port)
    server_address = ('127.0.0.1',port)
    httpd = HTTPServer(server_address,Server)
    print('running server on %i...'%port)
    httpd.serve_forever()
run()

