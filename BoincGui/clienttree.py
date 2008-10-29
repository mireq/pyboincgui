from PyQt4.QtGui import QTreeWidget, QTreeWidgetItem, QPixmap, QIcon
from PyQt4.QtCore import QAbstractItemModel, QModelIndex, QVariant, Qt, QString, QSize, SIGNAL, SLOT, QObject
import resources
from Boinc.interface import Interface

class clientTreeWidgetItem(QTreeWidgetItem):
	pass

class clientTreeWidget(QTreeWidget):
	#konstanty
	Client = 0

	def __init__(self, connManager, parent = None):
		QTreeWidget.__init__(self, parent)
		self.header().hide()
		self.connManager = connManager
		self.setIconSize(QSize(32, 32))
		self.connect(self.connManager, SIGNAL("clientAdded(int)"), self.addClient)
		self.connect(self.connManager, SIGNAL("clientRemoved(int)"), self.removeClient)

	def addClient(self, clId):
		item = clientTreeWidgetItem()
		item.setData(0, Qt.UserRole, QVariant(self.Client))
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
		icon = None
		name = conn.host()
		name = name + ':' + str(conn.port()) + " "
		if conn.connected() == Interface.connected:
			name = name + self.tr("(connected)")
			icon = QIcon(QPixmap(":connect_established.png"))
		elif conn.connected() == Interface.connecting:
			name = name + self.tr("(connecting)")
			icon = QIcon(QPixmap(":connect_creating.png"))
		elif conn.connected() == Interface.disconnected:
			name = name + self.tr("(disconnected)")
			icon = QIcon(QPixmap(":connect_no.png"))
		else:
			name = name + self.tr("(unauthorized)")
			icon = QIcon(QPixmap(":connect_no.png"))
		item.setData(0, Qt.DisplayRole, QVariant(name))
		if icon is None:
			item.setData(0, Qt.DecorationRole, QVariant())
		else:
			item.setData(0, Qt.DecorationRole, QVariant(icon))

	def removeClient(self, clId):
		item = self.topLevelItem(clId)
		if not item == None:
			self.removeItemWidget(item, 0)

