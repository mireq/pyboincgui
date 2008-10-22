from PyQt4.QtCore import QObject, QSettings

class ConnectionManager(QObject):

	connParams = []
	connection = []

	def saveConnections(self):
		pass

	def deleteConnection(self, connId):
		self.connParams.pop(connId)

	def addConnection(self, local, path, host, port, password):
		self.connParams.append({'local':local, 'path':path, 'host':host, 'port':port, 'password':password})
		self.saveConnections()
		return len(self.connParams) - 1