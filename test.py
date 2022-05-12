import socket, pickle			

# Define the port on which you want to connect
port = 12345			

# Create a socket object
s2 = socket.socket()	

# Define the port on which you want to connect			

# connect to the server on local computer
s2.connect(('127.0.0.1', port))

# receive data from the server and decoding to get the string.
print (s2.recv(1024).decode())
s2.send(pickle.dumps({'b': 'b' }))
s2.close()
	


