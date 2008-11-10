import socket
import sys
import thread
from Queue import Queue
import time
from threading import Thread, Lock

class BoincConnectionException(Exception):
	pass

class Connection:
	"""Pripojenie ku klientovi BOINC
	
	Tato trieda zabezpecuje len pripojenie ku klientovi.
	O veci ako autorizacia sa musi starat uzivatel tejto triedy."""

	__host = None
	__port = None
	__sock = None

	__sendQueue = None
	__callback = None

	__mutex = None
	__thread = None

	def __init__(self,  host,  port, queue, callback = None):
		self.__host = host
		self.__port = port
		self.__commLock = thread.allocate_lock()
		self.__queue = queue
		self.__callback = callback
		self.__sendQueue = Queue()
		self.__mutex = Lock()
		self.__thread = None
		thread.start_new_thread(self.connectThread, (callback, ))

	def disconnect(self):
		self.__mutex.acquire()
		#self.__thread.join()
		self.__thread = None
		self.__mutex.release()
		if not self.__sock is None:
			self.__sock.close()
			self.__sock = None

	def __del__(self):
		print("odpojene")

	def connectThread(self, callback):
		try:
			self.__sock = None
			time.sleep(0.5)
			self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		except socket.error, msg:
			sys.stderr.write("Error " + msg[1] + "\n")
			if not callback is None:
				callback(BoincConnectionException(msg[1]))
			return

		try:
			time.sleep(0.5)
			self.__sock.connect((self.__host,  self.__port))
		except socket.error, msg:
			self.__sock = None
			sys.stderr.write("Error " + msg[1] + "\n")
			if not callback is None:
				callback(BoincConnectionException(msg[1]))
			return

		self.__mutex.acquire()
		#thread.start_new_thread(self.sendDataThread, ())
		self.__thread = Thread(target = self.sendDataThread)
		self.__thread.start()
		self.__mutex.release()

	def sendData(self, data, recvHandler = None, *params):
		self.__sendQueue.put((data, recvHandler, params))

	def sendDataThread(self):
		while True:
			data, recvHandler, params = self.__sendQueue.get()
			try:
				if self.__sock is None:
					raise BoincConnectionException("Socket nebol nastaveny")

				data = data + "\003"
				sys.stdout.write("\033[1;32m"+data+"\033[0m\n")
				sys.stdout.flush()

				while len(data) > 0:
					time.sleep(0.03)
					ns = self.__sock.send(data)
					data = data[ns:]

				rec = self.__sock.recv(1024)
				if len(rec) == 0:
					self.__sock.close()
					self.__sock = None
					if not self.__callback is None:
						self.__callback(0)
					return

				string = rec
				while rec[-1] != "\003":
					time.sleep(0.03)
					rec = self.__sock.recv(1024)
					string = string + rec

				#sys.stdout.write("\033[1;33m"+string+"\033[0m\n")
				sys.stdout.flush()
				if not recvHandler is None:
					params = (string[:-1], ) + params
					recvHandler(*params)
			except Exception, msg:
				self.__queue.put(msg)
			self.__sendQueue.task_done()

