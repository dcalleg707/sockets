import select
import socket
import sys
import queue
import pickle
import os
import subprocess
import sys

# Create a TCP/IP socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setblocking(0)

# Bind the socket to the port
server_address = ('localhost', 10000)
print('starting up on {} port {}'.format(*server_address),
      file=sys.stderr)
server.bind(server_address)

def handleMessage(s, message):
        registerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        registerSocket.connect(('localhost', 10002))
        registerSocket.send(message)
        registerSocket.close()
        message = pickle.loads(message)
        print(message)
        if message['type'] == 'exec':
            appSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            appSocket.connect(('localhost', 10001))
            appSocket.send(pickle.dumps(message))
            data = appSocket.recv(1024)
            registerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            registerSocket.connect(('localhost', 10002))
            registerSocket.send(data)
            registerSocket.close()
            print(pickle.loads(data))
            appSocket.close()
            s.send(data)
        elif message['type'] == 'kill':
            os.kill(message['pid'], 9)
            s.send(pickle.dumps({'type': 'kill', 'status': 'success'}))
        elif message['type'] == 'close':
            appSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            appSocket.connect(('localhost', 10001))
            appSocket.send(pickle.dumps({'type': 'close', 'app': 'notepad'}))
            sys.exit(9)
            os._exit(9)

# Listen for incoming connections
server.listen(5)

inputs = [server]
outputs = []

while inputs:
    # Wait for at least one of the sockets to be
    # ready for processing
    readable, writable, exceptional = select.select(inputs,
                                                    outputs,
                                                    inputs,
                                                    1)
    print(len(inputs))
      # Handle inputs
    for s in readable:

        if s is server:
            # A "readable" socket is ready to accept a connection
            connection, client_address = s.accept()
            print('  connection from', client_address,
                  file=sys.stderr)
            connection.setblocking(0)
            inputs.append(connection)
        else:
            try:
                data = s.recv(1024)
            except:
                print('error')
                
            print(data)
            if data:   
                print('a') 
                handleMessage(s, data)

