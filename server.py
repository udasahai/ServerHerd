import asyncio,sys,time
import aiohttp,re 

released = {
		"Goloman" : 8888,
		"Hands" : 8889,
		"Holiday" : 8890,
		"Welsh" : 8891,
		"Wilkes" : 8892
	}


adjacencyList = {
		"Goloman": ["Hands", "Holiday", "Wilkes"],
		"Hands": ["Wilkes", "Goloman"]	,
		"Holiday": ["Welsh", "Wilkes", "Goloman"],
		"Wilkes": ["Goloman", "Hands", "Holiday"],
		"Welsh": ["Holiday"]

	}

clientInfo = dict()

def mySplitter(str):
	buffer = []
	temp = ""
	for i in str:
		if i!='\n':
			temp += i
		else: 
			buffer.append(temp)
			temp = "" 
	return buffer 

def remain(str): 
	str = str[::-1]
	temp = "" 
	for i in str:
		if i!= '\n':
			temp += i
		else: 
			break
	return (temp[::-1])


class EchoClientProtocol(asyncio.Protocol):
	def __init__(self, message):
		self.message = message

	def connection_made(self, transport):
		self.transport = transport
		transport.write(self.message.encode())
		print('Data sent: {!r}'.format(self.message))
		# self.transport.close()

	def connection_lost(self, exc):
		print('Closed concoction')
		self.transport.close()


class EchoServerClientProtocol(asyncio.Protocol):
	def connection_made(self, transport):
		peername = transport.get_extra_info('peername')
		print('Connection from {}'.format(peername))
		self.transport = transport
		self.buffer = ""


	def data_received(self, data):
		message = data.decode()
		print("recieved {}".format(message))
		message = message.replace('\r\n', '\n')
		self.buffer += message
		splits = mySplitter(self.buffer)
		if (splits==[]):
			return
		else: 
			for msg in splits:
				self.processData(msg)
				# print(msg.split(' '))
			self.buffer = remain(self.buffer)


	def processData(self, message):
		# data = message.split(' ')
		data = re.findall(r'[^ ]+', message)
		print("In processData {}".format(data))
		# print(message[3])
	 
		if data[0]=="IAMAT":
			timestamp = data[3]
			timestamp = time.time() - float(timestamp)
			skew = str(timestamp)

			if (timestamp > 0):
				skew = "+" + skew 
			else:
				skew = "-" + skew
			# print("{} {}".format(data[1],clientInfo["kiwi.cs.ucla.edu"][0]))
			formatted_string = "{} {} {} {} {} {}".format("AT",sys.argv[1], skew, data[1], data[2], data[3])
			clientInfo[data[1]] = formatted_string
			print("Sending: {}".format(formatted_string))
			msg = formatted_string + "\n"
			self.transport.write(msg.encode())
			self.propagate(formatted_string)
			
			return
		elif data[0]=="WHATSAT":
			domain = data[1]
			radius = int(data[2])
			num_entries = int(data[3])

			if domain in clientInfo:
				msg = clientInfo[domain] + "\n"
				self.transport.write(msg.encode())
				return
		elif data[0]=="AT":
			print("Propogation recieved {}".format(' '.join(data)))
			if data[3] in clientInfo:
				if clientInfo[data[3]]==message:
					print("Terminating Propogation")
					return

			clientInfo[data[3]] = message
			self.propagate(message)



		self.transport.write("? \n".encode()) 


	def propagate(self, message):
		for server in adjacencyList[sys.argv[1]]:
			print("Propogation for {}".format(server))
			try :
				msg = message
				msg += "\n"
				print(msg)
				coro = loop.create_connection(lambda: EchoClientProtocol(msg), '127.0.0.1', released[server])
				loop.create_task(coro)	
			except Exception as err: 
				print ("cant connect to server")




if __name__ == "__main__":

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
	for x in clientInfo:
		print(clientInfo[x]) 
	server.close()
	loop.run_until_complete(server.wait_closed())
	loop.close()


