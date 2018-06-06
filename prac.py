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


string = "Hello\n"

print(mySplitter(string))
print(mySplitter("Hello World"))
print()