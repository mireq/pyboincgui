from PyQt4.QtCore import QObject, QSettings, SIGNAL
from interface import Interface
from Boinc.connection import BoincConnectionException
from Boinc.interface import BoincCommException

class BoincConnectionStruct(QObject):
	def __init__(self, local, path, host, port, password):
		QObject.__init__(self)
		self.__local = local
		self.__path = path
		self.__host = host
		self.__port = port
		self.__password = password
		self.__connected = False
		self.bInterface = Interface(host, port, password)


	def boincConnect(self):
		self.bInterface.boincConnect(self.__connectStateChanged)

	def __connectStateChanged(self, state):
		if self.__connected != state:
			self.__connected = state
			self.emit(SIGNAL('connectStateChanged(bool)'), self.__connected)

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

class ConnectionManager(QObject):

	connections = []

	def saveConnections(self):
		pass

	def getConnection(self, index):
		return self.connections[index]

	def getConnections(self):
		return self.connections

	def removeConnection(self, connId):
		self.connections.pop(connId)
		self.emit(SIGNAL('clientRemoved(int)'), connId)

	def addConnection(self, local, path, host, port, password):
		self.connections.append(BoincConnectionStruct(local, path, host, port, password))
		self.saveConnections()
		self.emit(SIGNAL('clientAdded(int)'), len(self.connections) - 1)
		return len(self.connections) - 1