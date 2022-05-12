# Import socket module
import socket, pickle			

# Create a socket object
s = socket.socket()	

# Define the port on which you want to connect
port = 12345			

# connect to the server on local computer
s.connect(('127.0.0.1', port))

# receive data from the server and decoding to get the string.
print (s.recv(1024).decode())
s.send(pickle.dumps({'a': 'a' }))
# close the connection
s.close()	
# Create a socket object
s2 = socket.socket()	

# Define the port on which you want to connect			

# connect to the server on local computer
s2.connect(('127.0.0.1', port))

# receive data from the server and decoding to get the string.
print (s2.recv(1024).decode())
s2.send(pickle.dumps({'a': 'a' }))
s2.close()
	
