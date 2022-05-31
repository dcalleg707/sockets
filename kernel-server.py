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
# Create a TCP/IP socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setblocking(0)
server_address = ('localhost', 10000)
processes = {}
appStatus = False
fileManagerStatus = False
guiStatus = False

print('starting up on {} port {}'.format(*server_address))
server.bind(server_address)

def checkAppStatus():
    time.sleep(10)
    global appStatus
    localAppStatus = appStatus
    while True:
        if localAppStatus != appStatus:
            print(localAppStatus)
            appStatus = localAppStatus
            storeMessage({'type': 'appStatus', 'status': appStatus})
        try:
            data = sendToApp({'type': 'check', 'src': 'KRL', 'dst': 'APP'})
            if data['status'] == 'online':
                localAppStatus = True
        except socket.error:
            localAppStatus = False 
            print('app off')
        time.sleep(3)

def checkFileManagerStatus():
    global fileManagerStatus
    localfileManagerStatus = fileManagerStatus
    while True:
        if localfileManagerStatus != fileManagerStatus:
            print(localfileManagerStatus)
            fileManagerStatus = localfileManagerStatus
            storeMessage({'type': 'fileManagerStatus', 'status': fileManagerStatus})
        try:
            data = sendToRegister({'type': 'check', 'src': 'KRL', 'dst': 'FMR'})
            if data['status'] == 'online':
                localfileManagerStatus = True
        except socket.error:
            localfileManagerStatus = False 
            print('file manager off')
        time.sleep(5)

def checkGuiStatus():
    global guiStatus
    localGuiStatus = guiStatus
    while True:
        if localGuiStatus != guiStatus:
            print(localGuiStatus)
            guiStatus = localGuiStatus
            storeMessage({'type': 'guiStatus', 'status': guiStatus})
        try:
            data = sendToGui({'type': 'check', 'src': 'KRL', 'dst': 'GUI'})
            if data['status'] == 'online':
                localGuiStatus = True
        except socket.error:
            localGuiStatus = False 
            print('GUI off')
        time.sleep(5)

def storeMessage(message):
    global fileManagerStatus
    try:
        message = pickle.dumps({'type': 'store', 'message': message, 'src': 'KRL', 'dst': 'FMR'})
        storeSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        storeSocket.connect(('localhost', 10002))
        storeSocket.send(message)
        storeSocket.close()
    except socket.error:
        fileManagerStatus = False


def sendToApp(message):
    appSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    appSocket.connect(('localhost', 10001))
    appSocket.send(pickle.dumps(message))
    response = appSocket.recv(1024)
    appSocket.close()
    response = pickle.loads(response)
    storeMessage(response)
    print(response)
    return response

def sendToRegister(message):
    registerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    registerSocket.connect(('localhost', 10002))
    registerSocket.send(pickle.dumps(message))
    response = registerSocket.recv(1024)
    registerSocket.close()
    response = pickle.loads(response)
    storeMessage(response)
    print(response)
    return response

def sendToGui(message):
    guiSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    guiSocket.connect(('localhost', 10003))
    guiSocket.send(pickle.dumps(message))
    response = guiSocket.recv(1024)
    guiSocket.close()
    response = pickle.loads(response)
    storeMessage(response)
    print(response)
    return response



def handleMessage(s, message):
    global processes
    message = pickle.loads(message)
    storeMessage(message)
    print(message)
    if message['type'] == 'exec':
        appResponse = sendToApp(message)
        print(appResponse)
        if appResponse['status'] == 'success':
            try:
                processes[appResponse['app']].append(appResponse['pid'])
            except KeyError:
                processes[appResponse['app']] = [appResponse['pid']]
        print(processes)
        s.send(pickle.dumps(appResponse))
    elif message['type'] == 'kill':
        appResponse = sendToApp(message)
        print(appResponse)
        s.send(pickle.dumps(appResponse))
    elif message['type'] == 'createFolder':
        appResponse = sendToRegister(message)
        print(appResponse)
        s.send(pickle.dumps(appResponse))
    elif message['type'] == 'deleteFolder':
        appResponse = sendToRegister(message)
        print(appResponse)
        s.send(pickle.dumps(appResponse))
    elif message['type'] == 'check':
        answer = {'type': 'check', 'src': 'KRL', 'dst': 'APP', 'status': 'online'}
        storeMessage(answer)
        s.send(pickle.dumps(pickle.dumps(answer)))
    elif message['type'] == 'stop':
        appSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        appSocket.connect(('localhost', 10001))
        appSocket.send(pickle.dumps({'type': 'stop', 'src': 'KRL', 'dst': 'APP'}))
        registerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        registerSocket.connect(('localhost', 10002))
        registerSocket.send(pickle.dumps({'type': 'stop', 'src': 'KRL', 'dst': 'FMR'}))
        guiSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        guiSocket.connect(('localhost', 10003))
        guiSocket.send(pickle.dumps({'type': 'stop', 'src': 'KRL', 'dst': 'GUI'}))
        sys.exit(9)
        os._exit(9)

# Listen for incoming connections
server.listen(5)

inputs = [server]
outputs = []
message_queues = {}


print('Initializing app module')
subprocess.Popen('cmd /k ' + os.path.dirname(os.path.abspath(__file__)) + '/app-server.py')
time.sleep(1)
try:
    response = sendToApp(message = {'type': 'check', 'src': 'KRL', 'dst': 'APP'})
    if response['status'] == 'online':
        appStatus = True
except socket.error:
    
    print('app is not online')
    appStatus = False
    os._exit(status=9)
print('app module initialized')

print('Initializing file manager module')
subprocess.Popen('cmd /k ' + os.path.dirname(os.path.abspath(__file__)) + '/register-server.py')
time.sleep(1)
try:
    response = sendToRegister(message = {'type': 'check', 'src': 'KRL', 'dst': 'FMR'})
    if response['status'] == 'online':
        fileManagerStatus = True
except socket.error:
    print('file manager is not online')
    fileManagerStatus = False
    os._exit(status=9)
print('file manager initialized')

print('Initializing GUI module')
subprocess.Popen('cmd /k ' + os.path.dirname(os.path.abspath(__file__)) + '/GUI.py')
time.sleep(1)
try:
    response = sendToGui(message = {'type': 'check', 'src': 'KRL', 'dst': 'GUI'})
    if response['status'] == 'online':
        guiStatus = True
except socket.error:
    print('gui is not online')
    guiStatus = False
    os._exit(status=9)
print('gui initialized')


appCheck = threading.Thread(target=checkAppStatus)
appCheck.setDaemon(True)
appCheck.start()

while inputs:

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