import socket
import threading
import pickle

class ThreadedServer(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

    def listen(self):
        self.sock.listen(5)
        while True:
            client, address = self.sock.accept()
            client.settimeout(60)
            new_thread = threading.Thread(target = self.listenToClient,args = (client,address))
            new_thread.start()
            new_thread.join()

    def listenToClient(self, client, address):
        size = 1024
        while True:
            try:
                data = client.recv(size)
                if data:
                    # Set the response to echo back the recieved data 
                    response = data
                    print(data)
                    client.send(response)
                else:
                    raise error('Client disconnected')
            except:
                client.close()
                return False
    def manageMessage(self, message):
        message = pickle.loads(message)
        print(message)
        

if __name__ == "__main__":
    while True:
        port_num = 10000
        try:
            port_num = int(port_num)
            break
        except ValueError:
            pass

    ThreadedServer('',port_num).listen()