from PyQt4.QtGui import QTreeWidget, QTreeWidgetItem, QPixmap, QIcon, QSizePolicy, QPainter, QImage, QBrush, QColor
from PyQt4.QtCore import QAbstractItemModel, QVariant, Qt, QString, QSize, SIGNAL, SLOT, QObject, QSize, QCoreApplication, QRect
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
	def __lt__(self, iny):
		a = self.data(0, Qt.UserRole + 2).toInt()[0]
		b = iny.data(0, Qt.UserRole + 2).toInt()[0]
		if not a == b:
			return a < b
		else:
			return self.data(0, Qt.DisplayRole).toString() < iny.data(0, Qt.DisplayRole).toString()

class projectTreeWidgetItem(clientSubTreeWidgetItem):
	pass

class workunitTreeWidgetItem(QTreeWidgetItem):
	def __lt__(self, iny):
		a = self.data(0, Qt.UserRole + 2).toInt()[0]
		b = iny.data(0, Qt.UserRole + 2).toInt()[0]
		if not a == b:
			return a < b
		else:
			return self.data(0, Qt.DisplayRole).toString() < iny.data(0, Qt.DisplayRole).toString()

class clientTreeWidget(QTreeWidget):

	def __init__(self, connManager, parent = None):
		QTreeWidget.__init__(self, parent)
		self.sortItems(0, Qt.AscendingOrder)
		self.setSortingEnabled(True)
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
		self.emit(SIGNAL("showStatusBarMsg(QString)"), self.tr("Client added"))

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
		cpuItem.setData(0, Qt.UserRole + 2, QVariant(0))
		subitems.append(cpuItem)

		projectsItem = clientSubTreeWidgetItem()
		projectsItem.setData(0, Qt.DisplayRole, QVariant(self.tr("Projects")))
		projectsItem.setData(0, Qt.DecorationRole, QVariant(QIcon(QPixmap(":projects.png"))))
		projectsItem.setData(0, Qt.UserRole, QVariant("projects"))
		projectsItem.setData(0, Qt.UserRole + 2, QVariant(1))
		subitems.append(projectsItem)

		statisticsItem = clientSubTreeWidgetItem()
		statisticsItem.setData(0, Qt.DisplayRole, QVariant(self.tr("Statistics")))
		statisticsItem.setData(0, Qt.DecorationRole, QVariant(QIcon(QPixmap(":statistics.png"))))
		statisticsItem.setData(0, Qt.UserRole, QVariant("statistics"))
		statisticsItem.setData(0, Qt.UserRole + 2, QVariant(2))
		subitems.append(statisticsItem)

		filetransfersItem = clientSubTreeWidgetItem()
		filetransfersItem.setData(0, Qt.DisplayRole, QVariant(self.tr("File transfers")))
		filetransfersItem.setData(0, Qt.DecorationRole, QVariant(QIcon(QPixmap(":filetransfers.png"))))
		filetransfersItem.setData(0, Qt.UserRole, QVariant("filetransfers"))
		filetransfersItem.setData(0, Qt.UserRole + 2, QVariant(3))
		subitems.append(filetransfersItem)
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
		for poradie in range(treeItem.childCount()):
			if treeItem.child(poradie).data(0, Qt.UserRole).toString() == "project":
				self.__updateProject(conn.getProject(treeItem.child(poradie).data(0, Qt.UserRole + 1).toString()), treeItem.child(poradie))

	def __updateProject(self, project, uzol):
		pixmap = QPixmap(':project')
		emblem = None
		if project['dont_request_more_work']:
			emblem = QPixmap(':no_new_tasks.png')
		if project['suspended_via_gui']:
			emblem = QPixmap(':workunit_suspended.png')
		self.__addEmblem(pixmap, emblem)
		uzol.setData(0, Qt.DecorationRole, QVariant(QIcon(pixmap)))

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
			projectItem.setData(0, Qt.UserRole + 2, QVariant(4))
			pridat[i] = projectItem;
			self.emit(SIGNAL("showStatusBarMsg(QString)"), self.tr("Client added"))

		self.__removeSubNodeList(projektyUzol, odobrat)
		self.__addSubNodeList(projektyUzol, pridat)

		for poradie in range(projektyUzol.childCount()):
			self.__updateWorkUnitsList(projects, projektyUzol.child(poradie))


	def __updateWorkUnitsList(self, info, uzol):
		pridat  = []
		odobrat = []
		polozky = []
		resAct  = {}
		aktualizovat = {}

		for poradie in range(uzol.childCount()):
			polozka = uzol.child(poradie)
			polozky.append(polozka.data(0, Qt.UserRole + 1).toString())

		master_url = uzol.data(0, Qt.UserRole + 1).toString()
		for res in info['result']:
			if res['project_url'] == master_url:
				resAct[res['name']] = res
				aktualizovat[res['name']] = [res]


		k = resAct.keys()
		for poradie in range(uzol.childCount()):
			try:
				polozka = uzol.child(poradie)
				i = k.index(polozka.data(0, Qt.UserRole + 1).toString())
				try:
					aktualizovat[str(polozka.data(0, Qt.UserRole + 1).toString())].append(polozka)
				except KeyError:
					pass
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
			self.__updateWorkunit(projectItem, aktualizovat[pridat[i]][0])
			projectItem.setData(0, Qt.UserRole, QVariant("workunit"))
			projectItem.setData(0, Qt.UserRole + 1, QVariant(pridat[i]))
			pridat[i] = projectItem

		self.__updateWorkunits(aktualizovat)
		self.__removeSubNodeList(uzol, odobrat)
		self.__addSubNodeList(uzol, pridat)

	def __modifyProgressPixmap(self, pixmap, done):
		alpha = pixmap.alphaChannel()
		painter = QPainter()
		painter.begin(alpha)
		painter.setRenderHint(QPainter.Antialiasing)
		painter.setPen(Qt.white)
		painter.setBrush(QBrush(QColor(0, 0, 0, 196)))
		rect = QRect(int(float(pixmap.rect().width()) * (-0.5)), int(float(pixmap.rect().height()) * (-0.5)), pixmap.rect().width() * 2, pixmap.rect().height() * 2)
		painter.drawPie(rect, 1440, ((100 - done) * 360 * 16) / 100)
		painter.end()
		pixmap.setAlphaChannel(alpha)

	def __setProgressPixmapInactive(self, pixmap):
		alpha = pixmap.alphaChannel()
		painter = QPainter()
		painter.begin(alpha)
		painter.setBrush(QBrush(QColor(0, 0, 0, 196)))
		painter.drawRect(pixmap.rect())
		painter.end()
		pixmap.setAlphaChannel(alpha)

	def __updateWorkunit(self, item, workunit):
		pixmap = QPixmap(":workunit.png")

		status = int(workunit['state'])
		try:
			done = int(float(workunit['active_task']['fraction_done']) * 100.0)
			processStatus = int(workunit['active_task']['active_task_state'])
		except KeyError:
			processStatus = -1
			done = 0

		try:
			suspViaGui = workunit['suspended_via_gui']
			suspViaGui = True
		except KeyError:
			suspViaGui = False

		data = QVariant.fromList([QVariant(status), QVariant(processStatus), QVariant(done), QVariant(suspViaGui)])
		if data.toList() == item.data(0, Qt.UserRole + 3).toList():
			return
		item.setData(0, Qt.UserRole + 3, data)

		emblem = None
		if status == 1:
			emblem = QPixmap(":status_downloading.png")
			item.setData(0, Qt.UserRole + 2, QVariant(3))
			self.__setProgressPixmapInactive(pixmap)
		elif status == 2:
			if processStatus == 1:
				emblem = QPixmap(":status_running.png")
				item.setData(0, Qt.UserRole + 2, QVariant(0))
			elif (processStatus != -1) or (processStatus == 9):
				emblem = QPixmap(":status_suspended.png")
				item.setData(0, Qt.UserRole + 2, QVariant(4))
			else:
				item.setData(0, Qt.UserRole + 2, QVariant(5))
			if processStatus == -1:
				self.__setProgressPixmapInactive(pixmap)
			else:
				self.__modifyProgressPixmap(pixmap, done)

		elif status == 3:
			emblem = QPixmap(":status_error.png")
			item.setData(0, Qt.UserRole + 2, QVariant(7))
		elif status == 4:
			emblem = QPixmap(":status_uploading.png")
			item.setData(0, Qt.UserRole + 2, QVariant(2))
		elif status == 5:
			emblem = QPixmap(":status_uploaded.png")
			item.setData(0, Qt.UserRole + 2, QVariant(1))
		elif status == 6:
			emblem = QPixmap(":status_aborted.png")
			item.setData(0, Qt.UserRole + 2, QVariant(6))
		else:
			item.setData(0, Qt.UserRole + 2, QVariant(8))
			self.__setProgressPixmapInactive(pixmap)

		if (suspViaGui):
			emblem = QPixmap(":workunit_suspended.png")

		self.__addEmblem(pixmap, emblem)

		item.setData(0, Qt.DecorationRole, QVariant(QIcon(pixmap)))

	def __addEmblem(self, pixmap, emblem):
		if not emblem is None:
			painter = QPainter()
			painter.begin(pixmap)

			dest = emblem.rect()
			dest.translate(pixmap.rect().width()- emblem.rect().width(), pixmap.rect().height()- emblem.rect().height())

			painter.drawPixmap(dest, emblem, emblem.rect())
			painter.end()

	def __updateWorkunits(self, aktualizovat):
		keys = aktualizovat.keys()
		for key in keys:
			aktualizacia = aktualizovat[key]
			try:
				treeItem = aktualizacia[1]
				self.__updateWorkunit(treeItem, aktualizacia[0])
			except IndexError:
				pass

	def sizeHint(self):
		return QSize(250, 100)

