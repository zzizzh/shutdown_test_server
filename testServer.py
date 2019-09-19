
import time
import sys
import socket
import base64
import json

from threading import Thread

SERVER_PORT=11117
HOST_IP='127.0.0.1'
SERVER_IP='172.30.1.10'
BUF_SIZE=8192

class Shell(Thread):
	def __init__(self, server):
		Thread.__init__(self) 
		self.server=server
		
	def run(self):
		while True:
			print('select menu')
			print('1) : get clients')
			print('2) : shut down client')
			print('3) : shut down all client')

			ch=input()
			if ch=='1':
				client_list = self.server.getClientThreads()
				print(str(len(client_list)) + ' clients connected')
				for client in client_list:
					print('client id : ' + str(client.id))	
					print('client name : ' + client.name)

			elif ch=='2':
				client_list = self.server.getClientThreads()
				if len(client_list) == 0:
					print('there is no connected client')
					continue
				print('1) : select client')
				print('2) : back before menu')

				ch=input()

				if ch=='1':
					print('input client id : ')

					ch=input()

					client_list = self.server.getClientThreads()
					for client in client_list:
						if client.id == int(ch):
							client.setReady()
							print('shutdown ' + ch + ' client pc')
							continue

					print('there is no client id ' + ch)
					continue

				if ch=='2':
					continue

				else:
					print('you choose incorect menu num.')
					continue
			
			elif ch=='3':
				client_list = self.server.getClientThreads()
				for client in client_list:
					client.setReady()
					print('shutdown ' + client.name + ' pc')
					continue

			else:
				print('you choose incorect menu num.')
				continue
			
'''
main server has clientThread list
if connect client, make thread(Sender class) and and thread list(clientThreads)
and wait another connection from client
'''
class Server (Thread):

	def __init__(self, ip, port):
		Thread.__init__(self) 
		self.ip=ip
		self.port=port
		self.clientThreads=[]

		self.packets=[]
		self.clientNum=0

	def run(self):
		serverSocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		serverSocket.bind((self.ip, self.port))

		while True:
			print('wait client connect...')
			serverSocket.listen(0)
			clientSocket, addr=serverSocket.accept()

			print('client connect!')
			self.clientNum=self.clientNum+1
			clientThread=Client(self, clientSocket, self.clientNum)
			self.clientThreads.append(clientThread)
			clientThread.start()

	def getClientThreads(self):
		return self.clientThreads

	def getClientCount():
		return len(self.clientThreads)


'''
class that communicate with C# client
'''
class Client (Thread):

	def __init__(self, server, clientSocket, clientNum):
		Thread.__init__(self) 
		self.client=self
		self.clientSocket=clientSocket
		self.id=clientNum
		self.name=''
		self.server=server

		self.packet = {'IF_CODE' : 'SHUTDOWN', 'Client' : 'BACKEND/TEST', 'Type' : 'server' }
		self.ready=False

	def run(self):
		while True:
			data=self.clientSocket.recv(1024)

			if data:
				packet=data.decode('utf8')
				break

		packets=packet.split('<EOP')

		for str in packets:
			if str=='': break
			try:
				parse=json.loads(str)
			except:
				print(str+'\n> ', end='')
				continue

			if parse['IF_CODE']=='Device':
				print('client name : ' + parse['Client'])
				self.name=parse['Client']

		while True:
			if self.ready==True:
				self.networkWrite()
				self.server.getClientThreads().remove(self)
				self.clientSocket.close()
				return

	def networkWrite(self):
		str=json.dumps(self.packet)
		str+='<EOP>'
		bytes=str.encode('utf8')
		self.clientSocket.sendall(bytes)

	def setReady(self):
		self.ready=True

def main():
	server = Server(HOST_IP, SERVER_PORT)
	server.start()
	shell = Shell(server)
	shell.start()

if __name__ == '__main__':
    main()
