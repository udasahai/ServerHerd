import asyncio,sys,time
import aiohttp,re,json

released = {
		"Goloman" : 12451,
		"Hands" : 12446,
		"Holiday" : 12447,
		"Welsh" : 12448,
		"Wilkes" : 12450
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
		async with session.get(Url) as resp:
			JSON = (await resp.json())
			JSON['results'] = JSON['results'][:num_entries]
			JSON = (json.dumps(JSON, indent=4))
			JSON.replace('\n\n','\n')
			JSON.rstrip('\n')
			JSON += "\n\n"
			transport.write(JSON.encode())
			file.write("Sending JSON to Client \n {}".format(JSON))

class EchoClientProtocol(asyncio.Protocol):
	def __init__(self, message, server):
		self.message = message
		self.server = server

	def connection_made(self, transport):
		self.transport = transport
		transport.write(self.message.encode())
		file.write("New connection to Server {} \n".format(self.server))
		file.write("Sending to Server {}: {}".format(self.server,self.message))

		# self.transport.close()

	def connection_lost(self, exc):
		file.write('Closed connection to {} \n'.format(self.server))
		self.transport.close()


class EchoServerClientProtocol(asyncio.Protocol):
	def connection_made(self, transport):
		peername = transport.get_extra_info('peername')
		file.write('New Connection from {}\n'.format(peername))
		self.transport = transport
		self.buffer = ""

	def connection_lost(self, exc):
		file.write('Closed connection to {} \n'.format(self.transport.get_extra_info('peername')))



	def data_received(self, data):
		message = data.decode()
		file.write('Recieved: {}'.format(message))
		message = message.replace('\t', ' ')
		message = message.replace('\r\n', '\n')
		self.buffer += message
		splits = mySplitter(self.buffer)
		if (splits==[]):
			return
		else: 
			for msg in splits:
				self.processData(msg)
			self.buffer = remain(self.buffer)


	def processData(self, message):
		# data = message.split(' ')
		data = re.findall(r'[^ ]+', message)
	 
		if data[0]=="IAMAT" and len(data)==4:
			timestamp = data[3]
			timestamp = time.time() - float(timestamp)
			skew = str(timestamp)

			if (timestamp > 0):
				skew = "+" + skew 
			else:
				skew = "" + skew
			formatted_string = "{} {} {} {} {} {}".format("AT",sys.argv[1], skew, data[1], data[2], data[3])

			msg = formatted_string + "\n"
			self.transport.write(msg.encode())
			file.write("Sending to Client: {}".format(msg))

			if data[1] in clientInfo: 
				time_string = clientInfo[data[1]].split(' ')
				if float(data[3]) < float(time_string[5]):
					return


			clientInfo[data[1]] = formatted_string
			loop.create_task(self.propagate(formatted_string))
			
			return
		elif data[0]=="WHATSAT" and len(data)==4:
			if data[1] in clientInfo:
				domain = data[1]
				radius = int(data[2])*1000
				num_entries = int(data[3])
				location = clientInfo[domain]
				location = location.split(' ')
				location = lat_long(location[4])

				if domain in clientInfo:
					msg = clientInfo[domain] + "\n"
					self.transport.write(msg.encode())
					file.write("Sending location for {}: {}".format(domain,msg))
					loop.create_task(task_func(self.transport, num_entries, radius, location))
					return
		elif data[0]=="AT":

			if data[3] in clientInfo:
				stored = clientInfo[data[3]].split(' ')
				if clientInfo[data[3]]==message or float(data[5])<float(stored[5]):
					return

			clientInfo[data[3]] = message
			loop.create_task(self.propagate(message))
			return


		self.transport.write("? {}\n".format(message).encode()) 
		file.write("Sending to client: ? {}\n".format(message))

	async def propagate(self, message):
		for server in adjacencyList[sys.argv[1]]:
			try :
				msg = message
				msg += "\n"
				await loop.create_connection(lambda: EchoClientProtocol(msg,server), '127.0.0.1', released[server])
			except Exception as err: 
				file.write("Failed to connect to {} \n".format(server))





if __name__ == "__main__":

	file = open("{}.txt".format(sys.argv[1]),"a+")
	loop = asyncio.get_event_loop()
	file.write("Starting event loop\n")
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
	file.write("Closed event loop\n")
	file.close()

