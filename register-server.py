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
processes = {}

# Bind the socket to the port
server_address = ('localhost', 10002)
print('starting up on {} port {}'.format(*server_address),
      file=sys.stderr)
server.bind(server_address)

def handleMessage(s, message):
    message = pickle.loads(message)
    print(message)
    if message['type'] == 'createFolder':
        try:
            os.mkdir('./folders' + '/' + message['name'])
            s.send(pickle.dumps({'type': 'createFolder', 'status': 'success'}))
        except FileExistsError:
            s.send(pickle.dumps({'type': 'createFolder', 'status': 'failure'}))
    elif message['type'] == 'check':
        s.send(pickle.dumps({'type': 'check', 'status': 'online'}))
    elif message['type'] == 'close':
        sys.exit(9)
        os._exit(9)

# Listen for incoming connections
server.listen(5)

inputs = [server]
outputs = []
message_queues = {}

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