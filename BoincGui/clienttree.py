from PyQt4.QtGui import QTreeWidget, QTreeWidgetItem, QPixmap, QIcon, QSizePolicy
from PyQt4.QtCore import QAbstractItemModel, QVariant, Qt, QString, QSize, SIGNAL, SLOT, QObject, QSize, QCoreApplication
import resources
from Boinc.interface import Interface

class clientTreeWidgetItem(QTreeWidgetItem):
	__name = ""
	__state = Interface.disconnected
	def setName(self, name):
		self.__name = name
		self.__updateItem()

	def setState(self, state):
		self.__state = state
		self.__updateItem()

	def __updateItem(self):
		name = ""
		icon = None
		if self.__state == Interface.connected:
			name = self.__name + QCoreApplication.translate("clientTreeWidget", "(connected)")
			icon = QIcon(QPixmap(":connect_established.png"))
		elif self.__state == Interface.connecting:
			name = self.__name + QCoreApplication.translate("clientTreeWidget", "(connecting)")
			icon = QIcon(QPixmap(":connect_creating.png"))
		elif self.__state == Interface.disconnected:
			name = self.__name + QCoreApplication.translate("clientTreeWidget", "(disconnected)")
			icon = QIcon(QPixmap(":connect_no.png"))
		else:
			name = self.__name + QCoreApplication.translate("clientTreeWidget", "(unauthorized)")
			icon = QIcon(QPixmap(":connect_established.png"))
		self.setData(0, Qt.DisplayRole, QVariant(name))
		if icon is None:
			self.setData(0, Qt.DecorationRole, QVariant())
		else:
			self.setData(0, Qt.DecorationRole, QVariant(icon))

class clientSubTreeWidgetItem(QTreeWidgetItem):
	pass

class projectTreeWidgetItem(QTreeWidgetItem):
	pass

class workunitTreeWidgetItem(QTreeWidgetItem):
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
		self.connect(conn, SIGNAL("projectState(PyQt_PyObject)"), self.__updateProjectStatus)
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
		projectsItem.setData(0, Qt.DecorationRole, QVariant(QIcon(QPixmap(":stats.png"))))
		projectsItem.setData(0, Qt.UserRole, QVariant("projects"))
		subitems.append(projectsItem)
		return subitems

	def __removeSubNodes(self, item):
		self.__removeSubNodesRecurs(item)

	def __removeSubNodesRecurs(self, item):
		child = item.child(0)
		while not child is None:
			self.__removeSubNodesRecurs(child)
			item.removeChild(child)
			child = item.child(0)

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

		#if conn.connected() == Interface.connected:
			#name = name + self.tr("(connected)")
			#icon = QIcon(QPixmap(":connect_established.png"))
		#elif conn.connected() == Interface.connecting:
			#name = name + self.tr("(connecting)")
			#icon = QIcon(QPixmap(":connect_creating.png"))
		#elif conn.connected() == Interface.disconnected:
			#name = name + self.tr("(disconnected)")
			#icon = QIcon(QPixmap(":connect_no.png"))
		#else:
			#name = name + self.tr("(unauthorized)")
			#icon = QIcon(QPixmap(":connect_established.png"))
		#item.setData(0, Qt.DisplayRole, QVariant(name))
		#if icon is None:
			#item.setData(0, Qt.DecorationRole, QVariant())
		#else:
			#item.setData(0, Qt.DecorationRole, QVariant(icon))
		item.setName(name)
		item.setState(conn.connected())

	def removeClient(self, clId):
		item = self.topLevelItem(clId)
		self.__removeSubNodes(item)
		self.takeTopLevelItem(clId)

	def __updateProjectStatus(self, projects):
		conn = self.sender()
		treeItem = conn.treeItem
		self.__updateProjectsList(projects, treeItem)
		#for poradie in range(treeItem.childCount()):
			#potomok = treeItem.child(poradie)
			#if not potomok is None:
				#if potomok.data(0, Qt.UserRole).toString() == 'projects':
					#self.__updateProjectsList(projects, potomok)

	def __updateProjectsList(self, projects, projektyUzol):
		"""Zoznam poloziek ktore sa maju pridat - slovnik"""
		pridat  = []
		"""Zoznam poloziek ktore sa maju oodbrat - QTreeWidgetItem"""
		odobrat = []
		"""Zoznam projektov ktore su v zozname - string, master_url"""
		polozky = []
		"""Zoznam aktualnych projektov - string"""
		projAct = []

		for poradie in range(projektyUzol.childCount()):
			projekt = projektyUzol.child(poradie)
			polozky.append(projekt.data(0, Qt.UserRole + 1).toString())

		for projekt in projects['project']:
			projAct.append(projekt['master_url'])
			try:
				i = polozky.index(projekt['master_url'])
			except ValueError:
				pridat.append(projekt)

		for poradie in range(projektyUzol.childCount()):
			projekt = projektyUzol.child(poradie)
			if not projekt.data(0, Qt.UserRole) == 'project':
				continue
			try:
				i = projAct.index(projekt.data(0, Qt.UserRole + 1).toString())
			except ValueError:
				odobrat.append(projekt)

		for i in range(len(pridat)):
			projectItem = projectTreeWidgetItem()
			projectItem.setData(0, Qt.DisplayRole, QVariant(pridat[i]['project_name']))
			projectItem.setData(0, Qt.DecorationRole, QVariant(QIcon(QPixmap(":project.png"))))
			projectItem.setData(0, Qt.UserRole, QVariant("project"))
			projectItem.setData(0, Qt.UserRole + 1, QVariant(pridat[i]['master_url']))
			pridat[i] = projectItem;

		self.__removeSubNodeList(projektyUzol, odobrat)
		self.__addSubNodeList(projektyUzol, pridat)

		for poradie in range(projektyUzol.childCount()):
			self.__updateWorkUnitsList(projects, projektyUzol.child(poradie))


	def __updateWorkUnitsList(self, info, uzol):
		pridat  = []
		odobrat = []
		polozky = []
		resAct  = {}

		for poradie in range(uzol.childCount()):
			polozka = uzol.child(poradie)
			polozky.append(polozka.data(0, Qt.UserRole + 1).toString())

		master_url = uzol.data(0, Qt.UserRole + 1).toString()
		for res in info['result']:
			if res['project_url'] == master_url:
				resAct[res['name']] = res


		k = resAct.keys()
		for poradie in range(uzol.childCount()):
			try:
				polozka = uzol.child(poradie)
				i = k.index(polozka.data(0, Qt.UserRole + 1).toString())
			except ValueError:
				odobrat.append(polozka)

		for k in resAct.keys():
			try:
				i = polozky.index(k)
			except ValueError:
				pridat.append(k)

		for i in range(len(pridat)):
			projectItem = workunitTreeWidgetItem()
			projectItem.setData(0, Qt.DisplayRole, QVariant(pridat[i]))
			projectItem.setData(0, Qt.DecorationRole, QVariant(QIcon(QPixmap(":workunit.png"))))
			projectItem.setData(0, Qt.UserRole, QVariant("workunit"))
			projectItem.setData(0, Qt.UserRole + 1, QVariant(pridat[i]))
			pridat[i] = projectItem

		self.__removeSubNodeList(uzol, odobrat)
		self.__addSubNodeList(uzol, pridat)

	def sizeHint(self):
		return QSize(250, 100)

