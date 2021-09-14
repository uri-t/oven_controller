from datetime import datetime
import socket
import threading
import queue
from urllib.parse import urlparse
from urllib.parse import parse_qs
import json
import client

from controller import Controller
class Server:
    def run(self):
        # set up socket 
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        host = '127.0.0.1'
        port = 3500
        s.bind((host, port))
        
        s.listen(1)
        
        # set up queue for communicating with controller
        self.q = queue.Queue()

        self.t_controller = None
        stopped = False
        
        self.controller = Controller()

        while True:
            conn, addr = s.accept()
    
            data = conn.recv(10000)

            ts = []

            while True:
                try:
                    ts.append(self.q.get(block = False))
                except queue.Empty:
                    print("server: done reading!")
                    break

            conn.send(bytes(self.handle_request(data, temp_data = ts), 'utf-8'))

            conn.close()

    def header(self, headers):
        header_str = 'HTTP/2 200 OK\r\n'
        
        for field_name in headers:
            header_str += '%s: %s\r\n' % (field_name, headers[field_name])
            
        header_str += '\r\n'
        return header_str
    
    def start(self, params):
        print('starting controller')
        print(params)

        # process params
        ts = [float(params[key][0]) for key in sorted(params.keys()) if key[0] == 't']

        Ts = [float(params[key][0]) for key in sorted(params.keys()) if key[0] == 'T']

        print(ts)
        print(Ts)
        # stop controller if running
        if self.t_controller:
            self.controller.terminate()
            self.t_controller.join()
            self.controller = Controller()

        # start new controller
        f = open('results/%s.txt' % datetime.isoformat(datetime.now(), \
                                                       timespec='minutes'), 'a')
        
        self.t_controller = threading.Thread(target = self.controller.run_controller, \
                args = (ts, Ts), \
                kwargs = { 'read_callback': client.writer_fn(f),
                           'write_callback': client.write_duty_cycle,
                           'controller_fn': client.controller_fn(),
                           'temp_queue': self.q})
        self.t_controller.start()
        return self.header({}) + "<html></html>"
    
    def cancel(self):
        if self.controller:
            self.controller.terminate()
            self.t_controller.join()
            self.controller = Controller()

        return self.header({}) + "<html></html>"

    def serve(self, uri=None):
        fname = ""
        if uri:
            fname = uri.path[1:]
            
        if not (fname == 'index.html' or fname == 'script.js'):
            fname = 'index.html'
        
        f = open(fname)
        return self.header({}) + f.read()
    
    
    def temps(self, temp_data):
        response_str = ""
        t = [x[0] for x in temp_data]
        T = [x[1] for x in temp_data]
        return self.header({'Content-type': 'application/json'}) + json.dumps({'t_millis': t, 'temp_C': T})
    
    def handle_request(self, raw_data, temp_data=[]):
        request_lines = raw_data.decode().splitlines()
        uri = request_lines[0].split()[1]
        uri_parsed = urlparse(uri)
        params = parse_qs(uri_parsed.query)

        print(uri_parsed)
        
        if uri_parsed.path == '/cancel':
            return self.cancel()
        elif uri_parsed.path == '/start':
            return self.start(params)
        elif uri_parsed.path == '/temps.json':
            return self.temps(temp_data)
        else:
            return self.serve(uri_parsed)
        
        

Server().run()
