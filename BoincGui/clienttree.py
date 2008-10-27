from PyQt4.QtGui import QTreeWidget, QTreeWidgetItem, QPixmap, QIcon
from PyQt4.QtCore import QAbstractItemModel, QModelIndex, QVariant, Qt, QString, QSize, SIGNAL, SLOT

class clientTreeWidgetItem(QTreeWidgetItem):
	__connection = None
	def __init__(self, clId, connection):
		QTreeWidgetItem.__init__(self)
		self.__connection = connection;
		self.setData(0, Qt.DisplayRole, QVariant(self.name()))

	def name(self):
		name = self.__connection.host()
		name = name + ':' + str(self.__connection.port()) + ' ('
		if self.__connection.connected():
			name = name + "connected"
		else:
			name = name + "disconnected"
		name = name + ")"
		return name

	def changeConnectionState(self, state):
		self.setData(0, Qt.DisplayRole, QVariant(self.name()))

class clientTreeWidget(QTreeWidget):
	def __init__(self, connManager, parent = None):
		QTreeWidget.__init__(self, parent)
		self.connManager = connManager
		self.setIconSize(QSize(64, 64))
		self.connect(self.connManager, SIGNAL("clientAdded(int)"), self.addClient)
		self.connect(self.connManager, SIGNAL("clientRemoved(int)"), self.removeClient)

	def addClient(self, clId):
		item = clientTreeWidgetItem(clId, self.connManager.getConnection(clId))
		self.connect(self.connManager.getConnection(clId), SIGNAL("connectStateChanged(bool)"), item.changeConnectionState)
		self.addTopLevelItem(item)

	def removeClient(self, clId):
		item = self.topLevelItem(clId)
		if not item == None:
			self.removeItemWidget(item, 0)

