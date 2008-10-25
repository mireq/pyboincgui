from PyQt4.QtCore import QObject, QSettings, SIGNAL

class ConnectionInfo:
	def __init__(self, local, path, host, port, password):
		self.local = local
		self.path = path
		self.host = host
		self.port = port
		self.password = password

	def name(self):
		return self.host+":"+str(self.port)

class ConnectionManager(QObject):

	connections = []

	def saveConnections(self):
		pass

	def getConnections(self):
		return self.connections

	def removeConnection(self, connId):
		self.connections.pop(connId)
		self.emit(SIGNAL('clientRemoved(int)'), connId)

	def addConnection(self, local, path, host, port, password):
		self.connections.append(ConnectionInfo(local, path, host, port, password))
		self.saveConnections()
		self.emit(SIGNAL('clientAdded(int)'), len(self.connections) - 1)