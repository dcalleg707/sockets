# Import socket module
import socket
import pickle
import os
import time

# local host IP '127.0.0.1'
host = '127.0.0.1'

# Define the port on which you want to connect
port = 10001

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

# connect to server on local computer
s.connect((host,port))

# message you send to server
message = "shaurya says geeksforgeeks"

# message received from server
s.send(pickle.dumps({'type': 'close', 'app': 'notepad'}))
data = s.recv(1024)
data = pickle.loads(data)
time.sleep(5)
os.kill(data['pid'], 9)
# print the received message
# here it would be a reverse of sent message
print('Received from the server :',str(data))



    # ask the client whether he wants to continue
# close the connection
s.close()