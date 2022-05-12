# first of all import the socket library
import socket, pickle		

# next create a socket object
s = socket.socket()		
print ("Socket successfully created")

# reserve a port on your computer in our
# case it is 12345 but it can be anything
port = 12345			

# Next bind to the port
# we have not typed any ip in the ip field
# instead we have inputted an empty string
# this makes the server listen to requests
# coming from other computers on the network
s.bind(('', port))		
print ("socket binded to %s" %(port))

# put the socket into listening mode
s.listen(5)	
s.setblocking(False)
print ("socket is listening")		
cons = []
# a forever loop until we interrupt it or
# an error occurs
while True:
    # Establish connection with client.
    try:
        conn, addr = s.accept()                           
        conn.setblocking(False)	
        print ('Got connection from', addr )

        # send a thank you message to the client. encoding to send byte type.
        conn.send('Thank you for connecting'.encode())
        cons.append(conn)
        # Close the connection with the client
    except:
        pass
    
    try:
        for con in cons:
            print(pickle.loads(con.recv(1024)))
        # Close the connection with the client
    except:
        pass
