import asyncio,sys,time
import aiohttp,re,json

released = {
		"Goloman" : 12445,
		"Hands" : 12446,
		"Holiday" : 12447,
		"Welsh" : 12448,
		"Wilkes" : 12449
	}


adjacencyList = {
		"Goloman": ["Hands", "Holiday", "Wilkes"],
		"Hands": ["Wilkes", "Goloman"]	,
		"Holiday": ["Welsh", "Wilkes", "Goloman"],
		"Wilkes": ["Goloman", "Hands", "Holiday"],
		"Welsh": ["Holiday"]

	}
api_key = "AIzaSyBI3OVlE-w_AglAPw7M2hBCyPqKyAz_ibk"
url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

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

def lat_long(str):
	cords = []
	temp = ""
	for i in range(0,len(str)): 
		if str[i]=='+' or str[i]=='-':
			if i!=0:
				cords.append(temp)
				temp = ""
		temp += str[i]
	cords.append(temp)
	return ",".join(cords)


async def task_func(transport, num_entries, radius, location):
	async with aiohttp.ClientSession() as session:
		Url = '{}?location={}&radius={}&key={}'.format(url,location,radius,api_key)
		print(Url)
		async with session.get(Url) as resp:
			print(resp.url)
			JSON = (await resp.json())
			JSON['results'] = JSON['results'][:num_entries]
			JSON = (json.dumps(JSON, indent=4, sort_keys=True))
			JSON.replace('\n\n','\n')
			JSON.rstrip('\n')
			JSON += "\n\n"
			transport.write(JSON.encode())

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
			radius = int(data[2])*1000
			num_entries = int(data[3])
			location = clientInfo[domain]
			location = location.split(' ')
			location = lat_long(location[4])
			location.replace('+','')
			print(location)

			if domain in clientInfo:
				msg = clientInfo[domain] + "\n"
				self.transport.write(msg.encode())
				loop.create_task(task_func(self.transport, num_entries, radius, location))
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


