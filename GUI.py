import tkinter
from traceback import FrameSummary
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


ventana = tkinter.Tk()
ventana.geometry("1280x720")


bg = tkinter.PhotoImage(file="{}/img/Wallpaper.png".format(os.path.dirname(os.path.abspath(__file__))))
fondo = tkinter.Label(ventana,image=bg)
fondo.place(x=0,y=0)



carpetaCreada = tkinter.PhotoImage(file="{}/img/carpetaCreada.png".format(os.path.dirname(os.path.abspath(__file__))))
carpetaImg = tkinter.PhotoImage(file="{}/img/carpeta.png".format(os.path.dirname(os.path.abspath(__file__))))
blocImg = tkinter.PhotoImage(file="{}/img/bloc.png".format(os.path.dirname(os.path.abspath(__file__))))
apagarImg = tkinter.PhotoImage(file="{}/img/shutdown.png".format(os.path.dirname(os.path.abspath(__file__))))

row = 3
column = 0
nombreCarpeta = tkinter.Entry(ventana)

def crearCarpeta():
    nombreCarpeta.grid(row=0,column=4)
    botonCarpeta = tkinter.Button(ventana, text="Crear carpeta", command= lambda: crearIconoCarpeta(nombreCarpeta.get(),botonCarpeta))
    botonCarpeta.grid(row=1, column=4)

    

def crearIconoCarpeta(nombre,botonCarpeta):
    botonCarpeta.grid_remove()
    nombreCarpeta.grid_remove()
    global row, column
    print(nombre)
    kernelSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    kernelSocket.connect(('localhost', 10000))
    kernelSocket.send(pickle.dumps({'type': 'createFolder', 'name': nombre, 'src': 'GUI', 'dst': 'FMR'}))
    response = pickle.loads(kernelSocket.recv(1024))
    kernelSocket.close()
    if(response['status'] == 'success'):
        carpetaNueva = tkinter.Button(ventana, image=carpetaCreada, text=nombre, command=lambda:borrarCarpeta(carpetaNueva,nombre), compound="top")
        carpetaNueva.grid(row=row,column=column,padx=10,pady=20)
        row = row + 1
        if row == 7:
            row = 0
            column = column + 1
        print(row)
    else:
        print('error')

def borrarCarpeta(carpetaNueva,nombre):
    kernelSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    kernelSocket.connect(('localhost', 10000))
    kernelSocket.send(pickle.dumps({'type': 'deleteFolder', 'name': nombre, 'src': 'GUI', 'dst': 'FMR'}))
    response = pickle.loads(kernelSocket.recv(1024))
    kernelSocket.close()
    global row,column
    if(response['status']=='success'):
        carpetaNueva.destroy()
        if row > 0:
            row-=1
        elif row==0 and column==1:
            row = 6
            column = 0
        elif row==0 and column>0:
            row = 7
            column-=1
        print(row,column)
    else:
        print("error")


def cerrar():
    ventana.destroy()

boton1 = tkinter.Button(ventana, image=carpetaImg, text="Crear carpeta", command= crearCarpeta)
boton2 = tkinter.Button(ventana, image=blocImg, text="Abrir bloc")
boton3 = tkinter.Button(ventana, image= apagarImg, text="Apagar",command=cerrar)

boton1.grid(row=0,column=0,padx=10,pady=20)
boton2.grid(row=1,column=0,padx=10,pady=20)
boton3.grid(row=2,column=0,padx=10,pady=20)

# Create a TCP/IP socket

def checkAppStatus():
    global appStatus
    localAppStatus = appStatus
    while True:
        if localAppStatus != appStatus:
            print(localAppStatus)
            appStatus = localAppStatus
            storeMessage({'type': 'appStatus', 'status': appStatus})
        try:
            checkSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            checkSocket.connect(('localhost', 10001))
            checkSocket.send(pickle.dumps({'type': 'check'}))
            data = pickle.loads(checkSocket.recv(1024))
            if data['status'] == 'online':
                localAppStatus = True
                print('app is online')
            checkSocket.close()
        except socket.error:
            localAppStatus = False 
            print('app off')
        time.sleep(5)

def storeMessage(message):
    message = pickle.dumps(message)
    storeSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    storeSocket.connect(('localhost', 10002))
    storeSocket.send(message)
    storeSocket.close()

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
    elif message['type'] == 'check':
        s.send(pickle.dumps({'type': 'check', 'status': 'online', 'src': 'GUI', 'dst': message['src']}))
    elif message['type'] == 'close':
        sys.exit(9)
        os._exit(9)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setblocking(0)
server_address = ('localhost', 10003)
processes = {}
appStatus = False

print('starting up on {} port {}'.format(*server_address))
server.bind(server_address)

# Listen for incoming connections
server.listen(5)

inputs = [server]
outputs = []
message_queues = {}
"""
appCheck = threading.Thread(target=checkAppStatus)
appCheck.setDaemon(True)
appCheck.start()
"""

while inputs:
    ventana.update_idletasks()
    ventana.update()

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