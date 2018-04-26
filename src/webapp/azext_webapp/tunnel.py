import sys
import ssl
import socket
import time
import traceback
import websocket

from contextlib import closing
from threading import Thread
from websocket import create_connection, WebSocket

from knack.util import CLIError
from knack.log import get_logger
logger = get_logger(__name__)  # TODO: Replace print with logger below

class TunnelWebSocket(WebSocket):
    def recv_frame(self):
        frame = super(TunnelWebSocket, self).recv_frame()
        print('Received frame:{}'.format(frame))
        return frame
    
    def recv(self):
        data = super(TunnelWebSocket, self).recv()
        print('Received websocket data:{}'.format(data))
        return data

    def send_binary(self, data):
        super(TunnelWebSocket, self).send_binary(data)

class TunnelServer(object):
    def __init__(self, local_addr, local_port, remote_addr, remote_user_name, remote_password):
        self.local_addr = local_addr
        self.local_port = local_port
        if not self.is_port_open():
            raise CLIError('Defined port is currently unavailable')
        self.remote_addr = remote_addr
        self.remote_user_name = remote_user_name
        self.remote_password = remote_password
        print('Creating a socket')
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('Setting socket options')
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print('Binding to socket on local address and port')
        self.sock.bind((self.local_addr, self.local_port))
        print('Got to the end of init')

    def create_basic_auth(self):
        from base64 import b64encode, b64decode
        basic_auth_string = '{}:{}'.format(self.remote_user_name, self.remote_password).encode()
        basic_auth_string = b64encode(basic_auth_string).decode('utf-8')
        return basic_auth_string

    def is_port_open(self):
        is_port_open = False
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            if sock.connect_ex(('', self.local_port)) == 0:
                print('Port is open')
                is_port_open = True
            else:
                print('Port is not open')
            return is_port_open
    
    def is_port_set_to_default(self):
        import sys
        import certifi
        import urllib3
        try:
            import urllib3.contrib.pyopenssl
            urllib3.contrib.pyopenssl.inject_into_urllib3()
        except ImportError:
            pass
    
        http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
        headers = urllib3.util.make_headers(basic_auth='{0}:{1}'.format(self.remote_user_name, self.remote_password))
        url = 'https://{}{}'.format(self.remote_addr,'.scm.azurewebsites.net/AppServiceTunnel/Tunnel.ashx?GetStatus')
        r = http.request(
            'GET',
            url,
            headers=headers,
            preload_content=False
        )
        if r.status != 200:
            raise CLIError("Failed to connect to '{}' with status code '{}' and reason '{}'".format(url, r.status, r.reason))
        if '2222' in r.text:
            return True
        return False
        
        
    def listen(self):
        self.sock.listen(100)
        index = 0
        basic_auth_string = self.create_basic_auth()
        while True:
            self.client, address = self.sock.accept()
            self.client.settimeout(60)
            host = 'wss://{}{}'.format(self.remote_addr,'.scm.azurewebsites.net/AppServiceTunnel/Tunnel.ashx')
            basic_auth_header = 'Authorization: Basic {}'.format(basic_auth_string)
            websocket.enableTrace(True)
            self.ws = create_connection(host,
                                        sockopt = ((socket.IPPROTO_TCP, socket.TCP_NODELAY, 1),), 
                                        class_ = TunnelWebSocket, 
                                        header = [basic_auth_header], 
                                        sslopt={'cert_reqs': ssl.CERT_NONE}, 
                                        enable_multithread=True)
            print('websocket, connected status:{}', self.ws.connected)

            index = index + 1
            print('got debugger connection... index:{}'.format(index))
            debugger_thread = Thread(target = self.listen_to_client, args = (self.client, self.ws, index))
            web_socket_thread = Thread(target = self.listen_to_web_socket, args = (self.client, self.ws, index))
            debugger_thread.start()
            web_socket_thread.start()
            print('both threads started...')
            debugger_thread.join()
            web_socket_thread.join()
            print('both threads stopped...')

    def listen_to_web_socket(self, client, ws_socket, index):
        size = 4096
        while True:
            try:
                print('Waiting for websocket data, connection status:{}, index:{}'.format(ws_socket.connected, index))
                data = ws_socket.recv()
                print('Received websocket data:{}, index:{}'.format(data, index))
                if data:
                    # Set the response to echo back the recieved data 
                    response = data
                    print('Sending to debugger, response:{}, index{}'.format(response, index))
                    client.sendall(response)
                    print('Done sending to debugger, index:{}', index)
                else:
                    print('Client disconnected!, index:{}', index)
                    client.close()
                    ws_socket.close()                    
                    break
            except:
                traceback.print_exc(file=sys.stdout)
                client.close()
                ws_socket.close()
                return False

    def listen_to_client(self, client, ws_socket, index):
        size = 4096
        while True:
            try:
                print('Waiting for debugger data, index:{}'.format(index))
                buf = bytearray(4096)
                nbytes = client.recv_into(buf, 4096)
                print('Received debugger data, nbytes:{}, index:{}'.format(nbytes, index))
                if nbytes > 0:
                    responseData = buf[0:nbytes]
                    print('Sending to websocket, response data:{}, index:{}'.format(responseData, index))
                    ws_socket.send_binary(responseData)
                    print('Done sending to websocket, index:{}', index)
                else:
                    logger.warn('Client disconnected %s', index)
                    client.close()
                    ws_socket.close()
                    break
            except:
                traceback.print_exc(file=sys.stdout)
                client.close()
                ws_socket.close()
                return False

    def start_server(self):
        self.listen() 
