
import requests,time,json
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib
import argparse
parser = argparse.ArgumentParser(
    description='run node')
parser.add_argument('port',
                    help='port to run')
args = parser.parse_args()

def ask_for_data(n,key,client):
    params = urllib.parse.urlencode({
        'key':key,
        'client':client
    })
    path = 'http://'+n+'?'+params
    print('asking for data from',path)
    r = requests.get(path)

    if r.status_code==200:
        print("asking for data from %s success"%n)
        return r.text
    else:
        print(r.status_code)
        print(r,n)
        #return "ERROR"+str(r.status_code)
SELF = ''

class Server(BaseHTTPRequestHandler):
    # GET
    storage = {'1':"test_data"}
    neighbours = []
    def do_GET(s):
        print("<<==**\n Got connection:",s.path)
        params = s.get_params(s.path)
        print('params of conn',s.client_address,params)
        key = params['key'][0]
        if key =='nodes_':
            data = json.dumps(s.neighbours)
            s._send_resp(data)
            return
        client = params.get('client')
        #direct = False
        if not client:
            client = s.client_address[0]+':'+str(args.port)
        else:
            #client = client[0]
            nadr = s.client_address[0]+':'+str(args.port)
            client = s.client_address[0]+':'+str(args.port)
            # here we assume that port is the same
            if nadr not in s.neighbours:
                print('appending neighbour',nadr)
                s.neighbours+=[nadr]
            #direct = True
        data = s.storage.get(key) 
        print("data",data)
        if not data:
            # Data not found, start searching
            for n in s.neighbours:
                if n!=SELF and n!=client:
                    # do not ask the client itself
                    data = ask_for_data(n,key,SELF)
                    if data:
                        print("got data from",n,data)
                        s._send_resp(data)
                        return
            s._send_resp('NOTHING',400)
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

    def do_POST(s):
        print("<<==**\n Got post connection:",s.path)
        content_length = int(s.headers['Content-Length']) # <--- Gets the size of data
        post_data = s.rfile.read(content_length) # <--- Gets the data itself
        datastr = str(post_data.decode('utf-8'))
        print('***')
        print("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n"%(
                     str(s.path), str(s.headers),datastr))
        print('***')
        resp = ''
        try:
            parsed = json.loads(datastr)
            print (parsed)
            addr = parsed.get('node_addr')
            if addr:
                s.neighbours+=addr
                resp = 'list_upd'
            else:
                s.storage.update(parsed)
                resp = 'ok'
        except Exception as e:
            resp = e.message
        s._send_resp(resp)
        return

    def get_params(s,param_str):
        parsed  =urllib.parse.urlparse(param_str)
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
    port =  int(args.port) or 5000
    SELF = '0.0.0.0:'+str(port)
    server_address = ('0.0.0.0',port)
    httpd = HTTPServer(server_address,Server)
    print('running server on %i...'%port)
    httpd.serve_forever()
run()

