from PyQt4.QtGui import QTreeWidget, QTreeWidgetItem, QPixmap, QIcon
from PyQt4.QtCore import QAbstractItemModel, QModelIndex, QVariant, Qt, QString, QSize, SIGNAL, SLOT

class clientTreeWidgetItem(QTreeWidgetItem):
	def __init__(self, clId, connection):
		QTreeWidgetItem.__init__(self)
		self.setData(0, Qt.DisplayRole, QVariant(connection.name()))

class clientTreeWidget(QTreeWidget):
	def __init__(self, connManager, parent = None):
		QTreeWidget.__init__(self, parent)
		self.connManager = connManager
		self.setIconSize(QSize(64, 64))
		self.connect(self.connManager, SIGNAL("clientAdded(int)"), self.addClient)
		self.connect(self.connManager, SIGNAL("clientRemoved(int)"), self.removeClient)

	def addClient(self, clId):
		item = clientTreeWidgetItem(clId, self.connManager.getConnections()[clId])
		self.addTopLevelItem(item)

	def removeClient(self, clId):
		item = self.topLevelItem(clId)
		if not item == None:
			self.removeItemWidget(item, 0)

