from PyQt4.QtGui import QTreeWidget, QTreeWidgetItem, QPixmap, QIcon
from PyQt4.QtCore import QAbstractItemModel, QModelIndex, QVariant, Qt, QString, QSize, SIGNAL, SLOT, QObject

class clientTreeWidgetItem(QTreeWidgetItem):
	pass

class clientTreeWidget(QTreeWidget):
	def __init__(self, connManager, parent = None):
		QTreeWidget.__init__(self, parent)
		self.connManager = connManager
		self.setIconSize(QSize(64, 64))
		self.connect(self.connManager, SIGNAL("clientAdded(int)"), self.addClient)
		self.connect(self.connManager, SIGNAL("clientRemoved(int)"), self.removeClient)

	def addClient(self, clId):
		item = clientTreeWidgetItem()
		conn = self.connManager.getConnection(clId)
		conn.treeItem = item
		self.connect(conn, SIGNAL("connectStateChanged()"), self.__changeConnectionState)
		self.__changeConnectionState(conn)
		self.addTopLevelItem(item)

	def __changeConnectionState(self, cn = None):
		conn = None
		if cn is None:
			conn = self.sender()
		else:
			conn = cn
		item = conn.treeItem
		self.__clientItemData(conn, item)

	def __clientItemData(self, conn, item):
		name = conn.host()
		name = name + ':' + str(conn.port()) + " "
		if conn.connected():
			name = name + self.tr("(connected)")
		else:
			name = name + self.tr("(disconnected)")
		item.setData(0, Qt.DisplayRole, QVariant(name))

	def removeClient(self, clId):
		item = self.topLevelItem(clId)
		if not item == None:
			self.removeItemWidget(item, 0)

