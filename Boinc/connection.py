import socket
import sys
import thread
from Queue import Queue
import time
from threading import Thread, Lock

class BoincConnectionException(Exception):
	pass

class Connection:
	"""
	Pripojenie ku klientovi BOINC
	
	Tato trieda zabezpecuje len pripojenie ku klientovi.
	O veci ako autorizacia sa musi starat uzivatel tejto triedy.
	"""

	__host = None
	__port = None
	__sock = None

	
	__sendQueue = None
	__connStateCallback = None

	__mutex = None
	__thread = None

	__quit = False

	def __init__(self,  host,  port, errQueue, connStateCallback = None):
		"""
		Pripojenie sa k zvolenemu pc

		Host moze byt IP alebo dns adresa pocitaca. Dalej je potrebne uviest
		port na ktory sa pripajame a frontu do ktorej budu posielane chyby.
		Poslednym nepovinnym parametrom (connStateCallback je funkcia ktora
		sa bude volat v pripade zmeny stavu pripojenia)
		"""
		self.__host = host
		self.__port = port
		self.__commLock = thread.allocate_lock()
		self.__errQueue = errQueue
		self.__connStateCallback = connStateCallback
		self.__sendQueue = Queue()
		self.__mutex = Lock()
		self.__thread = None
		thread.start_new_thread(self.__connectThread, (connStateCallback, ))

	def disconnect(self):
		"""
		Odpojenie sa od klienta, cakanie na ukoncenie sietovych operacii.
		"""
		self.__quit = True
		self.__mutex.acquire()
		if not self.__thread is None:
			self.sendData("")
			self.__thread.join()
			self.__thread = None
			if not self.__sock is None:
				self.__sock.close()
		self.__mutex.release()


	def __connectThread(self, callback):
		"""
		Tato cast sa vykonava vo vlakne
		"""
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
		#thread.start_new_thread(self.__sendDataThread, ())
		self.__thread = Thread(target = self.__sendDataThread)
		self.__quit = False
		self.__thread.start()
		self.__mutex.release()

	def sendData(self, data, recvHandler = None, *params):
		"""
		Poslanie dat klientovi

		Prvym parametrom su data ktore chceme poslat. Dalsi parameter
		je funkcia ktora sa vola po odoslani. Dalsie parametre su volitelne
		parametre pre predchadzajucu funkciu. Tato funkcia nic neblokuje
		pretoze data vlozi do fronty a k samotnemu odoslaniu dojde neskor.
		"""
		self.__sendQueue.put((data, recvHandler, params))

	def __sendDataThread(self):
		"""
		Cyklicke odosielanie a prijem dat

		Ukoncenie sa da dosiahnut nastavenim atributu __quit na True a poslanim
		prazdneho stringu ("") metode sendData
		"""
		while True:
			data, recvHandler, params = self.__sendQueue.get()
			try:
				if self.__sock is None:
					raise BoincConnectionException("Socket nebol nastaveny")

				#koniec
				if self.__quit:
					return

				data = data + "\003"
				#sys.stdout.write("\033[1;32m"+data+"\033[0m\n")
				sys.stdout.flush()

				while len(data) > 0:
					time.sleep(0.01)
					ns = self.__sock.send(data)
					data = data[ns:]

					#koniec
					if self.__quit:
						return

				rec = self.__sock.recv(1024)
				if len(rec) == 0:
					self.__sock.close()
					self.__sock = None
					if not self.__connStateCallback is None:
						self.__connStateCallback(0)
					return

				#koniec
				if self.__quit:
					return

				string = rec
				while rec[-1] != "\003":
					time.sleep(0.01)
					rec = self.__sock.recv(1024)
					string = string + rec

					#koniec
					if self.__quit:
						return

				#sys.stdout.write("\033[1;33m"+string+"\033[0m\n")
				sys.stdout.flush()
				if not recvHandler is None:
					params = (string[:-1], ) + params
					recvHandler(*params)
			except Exception, msg:
				self.__errQueue.put(msg)
			self.__sendQueue.task_done()

