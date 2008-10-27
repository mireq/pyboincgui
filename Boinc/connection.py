import socket
import sys
import time
import thread

class BoincConnectionException(Exception):
	pass

class Connection:
	"""Pripojenie ku klientovi BOINC
	
	Tato trieda zabezpecuje len pripojenie ku klientovi.
	O veci ako autorizacia sa musi starat uzivatel tejto triedy."""

	__host = None
	__port = None
	__sock = None

	__commLock = None
	
	def __init__(self,  host,  port, queue):
		self.__host = host
		self.__port = port
		self.__commLock = thread.allocate_lock()
		self.__queue = queue
		try:
			self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			#time.sleep(1)
		except socket.error, msg:
			sys.stderr.write("Error " + msg[1] + "\n")
			raise BoincConnectionException(msg[1])

		try:
			self.__sock.connect((self.__host,  self.__port))
			#time.sleep(1)
		except socket.error, msg:
			sys.stderr.write("Error " + msg[1] + "\n")
			raise BoincConnectionException(msg[1])

	def __del__(self):
		if not self.__sock is None:
			self.__sock.close()
			self.__sock = None

	def sendData(self, data, recvHandler = None):
		thread.start_new_thread(self.sendDataThread, (data, recvHandler))

	def sendDataThread(self, data,  recvHandler):
		self.__commLock.acquire()
		try:
			time.sleep(1)
			data = data + "\003"
			print(data)
			while len(data) > 0:
				ns = self.__sock.send(data)
				data = data[ns:]
			time.sleep(1)
			rec = self.__sock.recv(1024)
			string = rec
			while rec[-1] != "\003":
				rec = self.__sock.recv(1024)
				string = string + recv
			print(string)
			if not recvHandler is None:
				recvHandler(string[:-1])
		except Exception, msg:
			self.__queue.put(msg)
		self.__commLock.release()

