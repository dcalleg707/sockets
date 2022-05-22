import socket
import threading
import pickle
import subprocess
import sys
import select

class ThreadedServer(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.setblocking(0)

    def listen(self):
        self.sock.listen(5)
        inputs = [self.sock]
        while True:
            readable, writable, exceptional = select.select(inputs, [], inputs, 1)
            for s in readable:
                if s is self.sock:
                    client, address = self.sock.accept()
                    new_thread = threading.Thread(target = self.listenToClient,args = (client,address))
                    new_thread.start()
                    new_thread.join()
            print('a')
    def listenToClient(self, client, address):
        size = 1024
        while True:
            try:
                data = client.recv(size)
                if data:
                    # Set the response to echo back the recieved data 
                    response = data
                    self.manageMessage(client, data)
                else:
                    raise error('Client disconnected')
            except:
                client.close()
                print('closed')
                return False

    def manageMessage(self, s, message):
        message = pickle.loads(message)
        print(message)
        if message['type'] == 'exec':
            if message['app'] == 'notepad':
                subp = subprocess.Popen(['notepad.exe'])
                s.send(pickle.dumps({'type': 'exec', 'app': 'notepad', 'status': 'success', 'pid': subp.pid}))
        elif message['type'] == 'kill':
            os.kill(message['pid'], 9)
            s.send(pickle.dumps({'type': 'kill', 'status': 'success'}))
        elif message['type'] == 'close':
            sys.exit(9)
            os._exit(9)


if __name__ == "__main__":
    while True:
        port_num = 10001
        try:
            port_num = int(port_num)
            break
        except ValueError:
            pass

    ThreadedServer('',port_num).listen()