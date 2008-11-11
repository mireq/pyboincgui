from PyQt4.QtCore import QObject, QSettings, SIGNAL, QTimer, QVariant
from interface import Interface
from Boinc.connection import BoincConnectionException
from Boinc.interface import BoincCommException
import Queue
import sys
import gc

class BoincConnectionStruct(QObject):

	def __init__(self, local, path, host, port, password, queue):
		QObject.__init__(self)
		self.__local = local
		self.__path = path
		self.__host = host
		self.__port = port
		self.__password = password
		self.__connected = 0
		self.__bInterface = Interface(host, port, password, queue)
		self.__updateTimer = None
		self.__projectState = None
		self.connect(self, SIGNAL('connectStateChanged(int)'), self.__updateConnectState)
		self.connect(self, SIGNAL('projectState(PyQt_PyObject)'), self.__startTimer)

	def local(self):
		return self.__local
	def path(self):
		return self.__path
	def host(self):
		return self.__host
	def port(self):
		return self.__port
	def password(self):
		return self.__password

	def __updateConnectState(self, state):
		if state == self.__bInterface.unauthorized or state == self.__bInterface.connected:
			if self.__updateTimer is None:
				self.__updateTimer = QTimer(self)
				self.connect(self.__updateTimer, SIGNAL('timeout()'), self.__startUpdateProjectState)
				self.__startUpdateProjectState()
		else:
			if not self.__updateTimer is None:
				self.__updateTimer.stop()
				self.__updateTimer = None

	def __startTimer(self):
		self.__updateTimer.start(1000)

	def projectState(self):
		return self.__projectState

	def __startUpdateProjectState(self):
		self.__updateTimer.stop()
		self.__bInterface.get_state(self.__updateProjectState)

	def __printTree(self, node, odsadenie = "  "):
		if type(node) == type({}):
			keys = node.keys()
			for key in keys:
				print(odsadenie + key + ":")
				self.__printTree(node[key], odsadenie + "  ")
			print(odsadenie + "------------")
		elif type(node) == type([]):
			print(odsadenie + '[')
			for child in node:
				self.__printTree(child, odsadenie + "  ")
			print(odsadenie + ']')
		else:
			print odsadenie+node

	def __createArr(self, slovnik, kluc):
		try:
			#prevedieme na pole
			if type(slovnik[kluc]) == type({}):
				val = slovnik[kluc]
				slovnik[kluc] = [val]
		except KeyError:
			slovnik[kluc] = []

	def __updateProjectState(self, st):
		self.__projectState = st
		self.__createArr(st, 'project')
		self.__createArr(st, 'workunit')
		self.__createArr(st, 'result')
		self.emit(SIGNAL("projectState(PyQt_PyObject)"), st)

	def getState(self):
		self.__bInterface.get_state(self.__recvState)

	def __recvState(self, data):
		self.emit(SIGNAL("getStateRecv(PyQt_PyObject)"), data)

	def boincConnect(self):
		self.__bInterface.boincConnect(self.__connectStateChanged)

	def __connectStateChanged(self, state):
		if self.__connected != state:
			self.__connected = state
			self.emit(SIGNAL('connectStateChanged(int)'), state)

	def boincDisconnect(self):
		if not self.__updateTimer is None:
			self.__updateTimer.stop()
			self.__updateTimer = None
		self.__bInterface.disconnect()
		self.__bInterface = None

	def local(self):
		return self.__local
	def path(self):
		return self.__path
	def host(self):
		return self.__host
	def port(self):
		return self.__port
	def password(self):
		return self.__password

	def connected(self):
		return self.__connected
	def bInterface(self):
		return self.__bInterface

class ConnectionManager(QObject):

	connections = []
	__queue = Queue.Queue()

	def saveConnections(self):
		settings = QSettings(self)
		settings.beginWriteArray("connections")
		for i in range(len(self.connections)):
			spojenie = self.connections[i]
			settings.setArrayIndex(i)
			settings.setValue("local", QVariant(bool(spojenie.local())))
			settings.setValue("path",  QVariant(str(spojenie.path())))
			settings.setValue("host",  QVariant(str(spojenie.host())))
			settings.setValue("port",  QVariant(int(spojenie.port())))
			settings.setValue("password", QVariant(str(spojenie.password())))
		settings.endArray()

	def loadConnections(self):
		settings = QSettings(self)
		velkost = settings.beginReadArray("connections")
		for i in range(velkost):
			settings.setArrayIndex(i)
			local = settings.value("local").toBool();
			path  = settings.value("path").toString();
			host  = settings.value("host").toString();
			port  = settings.value("port").toInt()[0];
			password = settings.value("password").toString()
			self.addConnection(local, path, host, port, password)
		settings.endArray()

	def getConnection(self, index):
		try:
			return self.connections[index]
		except IndexError:
			return None

	def getConnections(self):
		return self.connections

	def removeConnection(self, connId):
		if connId < len(self.connections):
			self.emit(SIGNAL('clientRemoved(int)'), connId)
			conn = self.connections.pop(connId)
			conn.boincDisconnect()
			conn = None
			self.saveConnections()

	def addConnection(self, local, path, host, port, password, autoConnect = True):
		conn = BoincConnectionStruct(local, path, host, port, password, self.__queue)
		self.connections.append(conn)
		self.saveConnections()
		self.emit(SIGNAL('clientAdded(int)'), len(self.connections) - 1)
		if autoConnect:
			conn.boincConnect()
		return len(self.connections) - 1

	def queue(self):
		return self.__queue

	def __del__(self):
		for conn in self.connections:
			self.emit(SIGNAL('clientRemoved(int)'), 0)
			conn.boincDisconnect()
		while True:
			try:
				self.connections.pop(0)
			except IndexError:
				return
	