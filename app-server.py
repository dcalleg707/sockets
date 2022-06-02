import select
import socket
import sys
import queue
import pickle
import os
import subprocess
import sys
import threading
import time
import signal
import random

# Create a TCP/IP socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setblocking(0)
processes = []
kernelStatus = True
die = False

# Bind the socket to the port
server_address = ('localhost', 10001)
print('starting up on {} port {}'.format(*server_address),
      file=sys.stderr)
server.bind(server_address)

def killAllProcesses():
    global processes
    for process in processes:
        try:
            os.kill(process, signal.SIGTERM)
        except:
            pass
    processes = []

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
    time.sleep(10)
    global kernelStatus
    global die
    localKernelStatus = kernelStatus
    while True:
        if localKernelStatus != kernelStatus:
            print(localKernelStatus)
            kernelStatus = localKernelStatus
        try:
            data = sendToKernel({'type': 'check', 'src': 'APP', 'dst': 'KRL'})
            if data['status'] == 'online':
                localKernelStatus = True
        except :
            localKernelStatus = False 
            die = True
        time.sleep(1)

def handleMessage(s, message):
    global processes, die
    message = pickle.loads(message)
    print(message)
    if message['type'] != 'stop' and message['type'] != 'check':
        randomNumber = random.randint(1, 4)
        if randomNumber == 4:
            s.send(pickle.dumps({'type': 'check', 'status': 'error', 'src': 'APP', 'dst': 'KRL', 'error': 'error'}))
            return
        elif randomNumber > 1:
            s.send(pickle.dumps({'type': 'check', 'status': 'pending' ,'src': 'APP', 'dst': 'KRL'}))
            time.sleep(randomNumber)
    if message['type'] == 'exec':
        if message['app'] == 'notepad':
            subp = subprocess.Popen(['notepad.exe'])
            processes.append(subp.pid)
            try: s.send(pickle.dumps({'type': 'exec', 'app': 'notepad', 'status': 'success', 'pid': subp.pid, 'src': 'APP', 'dst': 'GUI'}))
            except socket.error:
                print('error')
    elif message['type'] == 'kill':
        
        
        try: 
            os.kill(message['pid'], 9)
            s.send(pickle.dumps({'type': 'kill', 'status': 'success', 'src': 'GUI', 'dst': 'KRL'}))
        except socket.error:
            print('error')
        except OSError:
            s.send(pickle.dumps({'type': 'kill', 'status': 'success', 'src': 'GUI', 'dst': 'KRL'}))
    elif message['type'] == 'check':
        try: s.send(pickle.dumps({'type': 'check', 'status': 'online', 'src': 'GUI', 'dst': 'KRL'}))
        except socket.error:
            print('error')
    elif message['type'] == 'stop':
        killAllProcesses()
        sys.exit(9)
        os._exit(9)
    elif message['type'] == 'stopApp':
        die = True

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
        killAllProcesses()
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