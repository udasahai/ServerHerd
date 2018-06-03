import asyncio,sys,time

class EchoServerClientProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        print('Connection from {}'.format(peername))
        self.transport = transport

    def data_received(self, data):
    	message = data.decode() 
    	data = processData(message).encode() 
    	self.transport.write(data)

    	print("Close the client socket")
    	self.transport.close() 


  #   	message = data.decode()
		# data = processData(message).encode()
  #       self.transport.write(data)
		
		# print('Close the client socket')
		# self.transport.close()


released = {
		"Goloman" : 8888,
		"Hands" : 2008,
		"Holiday" : 2009,
		"Welsh" : 2010,
		"Wilkes" : 2011
	}


def processData(message):
	data = message.split(' ')
	print(data)
	# print(message[3])

	timestamp = data[3]
	timestamp = time.time() - float(timestamp)
	skew = str(timestamp)

	if (timestamp > 0):
		skew = "+" + skew 
	else:
		skew = "-" + skew 

	if data[0]=="IAMAT":
		formatted_string = "{} {} {} {} {} {}".format("AT",sys.argv[1], skew, data[1], data[2], data[3])
		return formatted_string
	elif data[0]=="WHATSAT":
		domain = data[1]
		radius = int(data[2])
		num_entries = int(data[3])
		return "WHATSAT"
	else:
		return "? " 





loop = asyncio.get_event_loop()
# Each client connection will create a new protocol instance
coro = loop.create_server(EchoServerClientProtocol, '127.0.0.1', released[sys.argv[1]])
server = loop.run_until_complete(coro)

# Serve requests until Ctrl+C is pressed
print('Serving on {}'.format(server.sockets[0].getsockname()))
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

# Close the server
server.close()
loop.run_until_complete(server.wait_closed())
loop.close()