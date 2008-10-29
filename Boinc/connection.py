import socket
import sys
import thread
from Queue import Queue
import time

class BoincConnectionException(Exception):
	pass

class Connection:
	"""Pripojenie ku klientovi BOINC
	
	Tato trieda zabezpecuje len pripojenie ku klientovi.
	O veci ako autorizacia sa musi starat uzivatel tejto triedy."""

	__host = None
	__port = None
	__sock = None

	__sendQueue = Queue()
	
	def __init__(self,  host,  port, queue, callback = None):
		self.__host = host
		self.__port = port
		self.__commLock = thread.allocate_lock()
		self.__queue = queue
		time.sleep(0.3)
		thread.start_new_thread(self.connectThread, (callback, ))


	def __del__(self):
		if not self.__sock is None:
			self.__sock.close()
			self.__sock = None

	def connectThread(self, callback):
		try:
			self.__sock = None
			time.sleep(0.3)
			self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		except socket.error, msg:
			sys.stderr.write("Error " + msg[1] + "\n")
			if not callback is None:
				callback(BoincConnectionException(msg[1]))
			return

		try:
			time.sleep(0.3)
			self.__sock.connect((self.__host,  self.__port))
		except socket.error, msg:
			self.__sock = None
			sys.stderr.write("Error " + msg[1] + "\n")
			if not callback is None:
				callback(BoincConnectionException(msg[1]))
			return

		thread.start_new_thread(self.sendDataThread, ())

	def sendData(self, data, recvHandler = None):
		self.__sendQueue.put((data, recvHandler))

	def sendDataThread(self):
		while True:
			(data, recvHandler) = self.__sendQueue.get()
			try:
				if self.__sock is None:
					raise BoincConnectionException("Socket nebol nastaveny")
				data = data + "\003"
				print(data)
				while len(data) > 0:
					time.sleep(0.3)
					ns = self.__sock.send(data)
					data = data[ns:]
				rec = self.__sock.recv(1024)
				string = rec
				while rec[-1] != "\003":
					time.sleep(0.3)
					rec = self.__sock.recv(1024)
					string = string + recv
				print(string)
				if not recvHandler is None:
					recvHandler(string[:-1])
			except Exception, msg:
				self.__queue.put(msg)
			self.__sendQueue.task_done()

