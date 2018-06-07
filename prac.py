# import aiohttp
# import asyncio

# async def fetch(client):
#     async with client.get('http://python.org') as resp:
#         assert resp.status == 200
#         return await resp.text()

# async def main():
#     async with aiohttp.ClientSession() as client:
#         html = await fetch(client)
#         print(html)

# loop = asyncio.get_event_loop()
# loop.run_until_complete(main())

import logging


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

def complex_algorithm(items):
    for i in range(1,10):
        # do some complex algorithm computation
        file.write("{}\n".format(i))



file = open("hello.log", 'a+')
file.write("Hello World")

complex_algorithm(2)


