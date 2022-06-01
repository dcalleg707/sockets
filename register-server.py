import select
import socket
import sys
import queue
import pickle
import os
import json
from datetime import date
from time import strftime
import subprocess
import sys
import threading
import time

# Create a TCP/IP socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setblocking(0)
processes = {}
kernelStatus = False
die = False

# Bind the socket to the port
server_address = ('localhost', 10002)
print('starting up on {} port {}'.format(*server_address),
      file=sys.stderr)
server.bind(server_address)

def sendToKernel(message):
    try:
        appSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        appSocket.connect(('localhost', 10000))
        appSocket.send(pickle.dumps(message))
        response = appSocket.recv(1024)
        appSocket.close()
        response = pickle.loads(response)
        print(response)
        return response
    except:
        print('error')

def checkKernelStatus():
    global kernelStatus
    global die
    time.sleep(10)
    localKernelStatus = kernelStatus
    while True:
        if localKernelStatus != kernelStatus:
            print(localKernelStatus)
            kernelStatus = localKernelStatus
        try:
            data = sendToKernel({'type': 'check', 'src': 'APP', 'dst': 'KRL'})
            if data['status'] == 'online':
                localKernelStatus = True
        except:
            localKernelStatus = False 
            print('kernel off')
            die = True
        time.sleep(1)

def handleMessage(s, message):
    message = pickle.loads(message)
    print(message)
    if message['type'] == 'createFolder':
        try:
            os.mkdir(os.path.dirname(os.path.abspath(__file__)) +'/folders/' + message['name'])
            s.send(pickle.dumps({'type': 'createFolder', 'status': 'success', 'name': message['name'], 'src': 'FMR', 'dst': 'GUI'}))
        except FileExistsError:
            s.send(pickle.dumps({'type': 'createFolder', 'status': 'failure', 'name': message['name'], 'src': 'FMR', 'dst': 'GUI'}))
    elif message['type'] == 'check':
        try: s.send(pickle.dumps({'type': 'check', 'status': 'online', 'src': 'FMR', 'dst': 'KRL'}))
        except socket.error:
            sys.exit(9)
            os._exit(9)
    elif message['type'] == 'close':
        sys.exit(9)
        os._exit(9)
    elif message['type'] == 'store':
        try:
            fecha = date.today()
            message['message']['date'] = fecha.strftime("%m/%d/%Y")
            strm = str(message['message'])
            jsonprueba = json.dumps(strm)
            entry = json.loads(jsonprueba)

            if not os.path.exists('logs.txt'):
                f = open('logs.txt','x')
                f.write('[]')
                f.close()
            
            f = open('logs.txt','r')
            data = json.load(f)
            data.append(entry)
            f = open('logs.txt','w')
            json.dump(data,f,indent=4)
            f.close()
            
            s.send(pickle.dumps({'type': 'store', 'status': 'success', 'src': 'FMR', 'dst': 'GUI'}))
        except socket.error:
            print('error')
            

    elif message['type'] == 'deleteFolder':
        try:
            os.rmdir(os.path.dirname(os.path.abspath(__file__))+"/folders/"+message['name'])
            s.send(pickle.dumps({'type': 'deleteFolder', 'status': 'success', 'name': message['name'], 'src': 'FMR', 'dst': 'GUI'}))
        except:
            s.send(pickle.dumps({'type': 'deleteFolder', 'status': 'failure', 'name': message['name'], 'src': 'FMR', 'dst': 'GUI'}))
        

# Listen for incoming connections
server.listen(5)

inputs = [server]
outputs = []
message_queues = {}

kernelCheck = threading.Thread(target=checkKernelStatus)
kernelCheck.setDaemon(True)
kernelCheck.start()

while inputs:

    if die:
        sys.exit(9)
        os._exit(9)
    # Wait for at least one of the sockets to be
    # ready for processing
    readable, writable, exceptional = select.select(inputs,
                                                    outputs,
                                                    inputs,
                                                    0)
      # Handle inputs
    for s in readable:

        if s is server:
            # A "readable" socket is ready to accept a connection
            connection, client_address = s.accept()
            print('  connection from', client_address,
                  file=sys.stderr)
            connection.setblocking(0)
            inputs.append(connection)

            # Give the connection a queue for data
            # we want to send
            message_queues[connection] = queue.Queue()
        else:
            data = s.recv(1024)
            if data:
                # A readable client socket has data
                message_queues[s].put(data)
                # Add output channel for response
                if s not in outputs:
                    outputs.append(s)

    for s in writable:
        try:
            next_msg = message_queues[s].get_nowait()
        except queue.Empty:
            # No messages waiting so stop checking
            # for writability.
            print('  ', s.getpeername(), 'queue empty',
                  file=sys.stderr)
            outputs.remove(s)
        else:
            handleMessage(s, next_msg)
            outputs.remove(s)
            inputs.remove(s)
            del message_queues[s]
    
    for s in exceptional:
        print('exception condition on', s.getpeername(),
              file=sys.stderr)
        # Stop listening for input on the connection
        inputs.remove(s)
        if s in outputs:
            outputs.remove(s)
        s.close()

        # Remove message queue
        del message_queues[s]