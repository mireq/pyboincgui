from PyQt4.QtGui import QTreeWidget, QTreeWidgetItem, QPixmap, QIcon, QSizePolicy
from PyQt4.QtCore import QAbstractItemModel, QVariant, Qt, QString, QSize, SIGNAL, SLOT, QObject, QSize
import resources
from Boinc.interface import Interface

class clientTreeWidgetItem(QTreeWidgetItem):
	pass

class clientSubTreeWidgetItem(QTreeWidgetItem):
	pass

class projectTreeWidgetItem(QTreeWidgetItem):
	pass

class clientTreeWidget(QTreeWidget):

	def __init__(self, connManager, parent = None):
		QTreeWidget.__init__(self, parent)
		self.header().hide()
		self.setColumnCount(1)
		self.connManager = connManager
		self.setIconSize(QSize(32, 32))
		self.connect(self.connManager, SIGNAL("clientAdded(int)"), self.addClient)
		self.connect(self.connManager, SIGNAL("clientRemoved(int)"), self.removeClient)
		self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)

	def addClient(self, clId):
		item = clientTreeWidgetItem(self)
		item.setData(0, Qt.UserRole, QVariant("client"))
		conn = self.connManager.getConnection(clId)
		conn.treeItem = item
		self.connect(conn, SIGNAL("connectStateChanged(int)"), self.__changeConnectionState)
		self.connect(conn, SIGNAL("projectStatus(PyQt_PyObject)"), self.__updateProjectStatus)
		self.__changeConnectionState(conn.connected(), conn)
		self.addTopLevelItem(item)

	def __changeConnectionState(self, s, cn = None):
		conn = None
		if cn is None:
			conn = self.sender()
		else:
			conn = cn
		item = conn.treeItem
		self.__clientItemData(conn, item)
		self.__updateSubItems(item, conn)

	def __updateSubItems(self, item, conn):
		connectedState = conn.connected()
		if connectedState == 2 or connectedState == -1:
			self.__removeSubNodes(item)
			subNodes = self.__createClientSubNodes(item, conn)
			self.__addSubNodeList(item, subNodes)
		else:
			self.__removeSubNodes(item)

	def __createClientSubNodes(self, rodic, conn):
		subitems = []
		cpuItem = clientSubTreeWidgetItem()
		cpuItem.setData(0, Qt.DisplayRole, QVariant(self.tr("CPU")))
		cpuItem.setData(0, Qt.DecorationRole, QVariant(QIcon(QPixmap(":cpu.png"))))
		cpuItem.setData(0, Qt.UserRole, QVariant("cpu"))
		subitems.append(cpuItem)

		projectsItem = clientSubTreeWidgetItem()
		projectsItem.setData(0, Qt.DisplayRole, QVariant(self.tr("Projects")))
		projectsItem.setData(0, Qt.DecorationRole, QVariant(QIcon(QPixmap(":projects.png"))))
		projectsItem.setData(0, Qt.UserRole, QVariant("projects"))
		subitems.append(projectsItem)
		return subitems

	def __removeSubNodes(self, item):
		child = item.takeChild(0)
		while not child is None:
			item.removeChild(child)
			child = item.takeChild(0)

	def __addSubNodeList(self, item, subNodes):
		if len(subNodes) > 0:
			self.setUpdatesEnabled(False)
			item.addChildren(subNodes)
			item.setExpanded(True)
			self.setUpdatesEnabled(True)

	def __removeSubNodeList(self, rodic, odstranit):
		self.setUpdatesEnabled(False)
		for potomok in odstranit:
			rodic.removeChild(potomok)
		self.setUpdatesEnabled(True)

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
			icon = QIcon(QPixmap(":connect_established.png"))
		item.setData(0, Qt.DisplayRole, QVariant(name))
		if icon is None:
			item.setData(0, Qt.DecorationRole, QVariant())
		else:
			item.setData(0, Qt.DecorationRole, QVariant(icon))

	def removeClient(self, clId):
		self.takeTopLevelItem(clId)

	def __updateProjectStatus(self, projects):
		conn = self.sender()
		treeItem = conn.treeItem
		for poradie in range(treeItem.childCount()):
			potomok = treeItem.child(poradie)
			if not potomok is None:
				if potomok.data(0, Qt.UserRole).toString() == 'projects':
					self.__updateProjectsList(projects, potomok)

	def __updateProjectsList(self, projects, projektyUzol):
		pridat  = []
		"""Zoznam poloziek ktore sa maju pridat - slovnik"""
		odobrat = []
		"""Zoznam poloziek ktore sa maju oodbrat - QTreeWidgetItem"""
		polozky = []
		"""Zoznam projektov ktore su v zozname - string, master_url"""
		zozProj = []
		"""Zoznam aktualnych projektov - string"""

		for poradie in range(projektyUzol.childCount()):
			projekt = projektyUzol.child(poradie)
			polozky.append(projekt.data(0, Qt.UserRole).toString())

		for projekt in projects:
			zozProj.append(projekt['master_url'])
			try:
				i = polozky.index(projekt['master_url'])
			except ValueError:
				pridat.append(projekt)

		for poradie in range(projektyUzol.childCount()):
			projekt = projektyUzol.child(poradie)
			try:
				i = zozProj.index(projekt.data(0, Qt.UserRole).toString())
			except ValueError:
				odobrat.append(projekt)

		for i in range(len(pridat)):
			projectItem = projectTreeWidgetItem()
			projectItem.setData(0, Qt.DisplayRole, QVariant(pridat[i]['project_name']))
			projectItem.setData(0, Qt.DecorationRole, QVariant(QIcon(QPixmap(":workunit.png"))))
			projectItem.setData(0, Qt.UserRole, QVariant(pridat[i]['master_url']))
			pridat[i] = projectItem;

		self.__removeSubNodeList(projektyUzol, odobrat)
		self.__addSubNodeList(projektyUzol, pridat)

	def sizeHint(self):
		return QSize(250, 100)

