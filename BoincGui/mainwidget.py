from PyQt4.QtGui import QWidget, QHBoxLayout, QTableView, QTreeView, QStackedWidget, QLabel
from PyQt4.QtCore import QSize, SIGNAL, Qt, QString
from clienttree import clientTreeWidget
import InfoWidgets

class infoStackWidget(QStackedWidget):
	currentWidget = None

	def __init__(self, parent = None):
		QStackedWidget.__init__(self, parent)

	def setWidget(self, widget):
		self.unsetWidget()
		self.addWidget(widget)
		self.setCurrentWidget(widget)
		self.currentWidget = widget

	def unsetWidget(self):
		if not self.currentWidget is None:
			self.removeWidget(self.currentWidget)
			#self.currentWidget.setParent(None)
			self.currentWidget.deleteLater()
		self.currentWidget = None

class mainWidget(QWidget):
	def __init__(self, connManager, parent = None):
		QWidget.__init__(self, parent)
		self.layout = QHBoxLayout()
		self.setLayout(self.layout)

		self.tree = clientTreeWidget(connManager)
		self.infoWidget = infoStackWidget()

		self.layout.addWidget(self.tree)
		self.layout.addWidget(self.infoWidget)

		self.connect(self.tree, SIGNAL("currentItemChanged(QTreeWidgetItem *, QTreeWidgetItem *)"), self.changeActive)
		self.connect(self.tree, SIGNAL("showStatusBarMsg(QString)"), self.emitStatusBarMsg)

	def emitStatusBarMsg(self, msg):
		self.emit(SIGNAL("showStatusBarMsg(QString)"), msg)

	def changeActive(self, next, prev):
		if next is None:
			self.infoWidget.unsetWidget()
			self.emit(SIGNAL('clientChanged(int)'), -1)
			return

		polozka = next
		cesta = []
		while self.tree.indexFromItem(polozka).isValid():
			cesta.append(polozka)
			polozka = self.tree.itemFromIndex(self.tree.indexFromItem(polozka).parent())
		cesta.reverse()

		index = 0
		connection = None
		if len(cesta) >= 1:
			index = self.tree.indexOfTopLevelItem(cesta[0])
			connection = self.parent().connManager().getConnection(index)
			self.emit(SIGNAL('clientChanged(int)'), index)
			if connection is None:
				self.infoWidget.unsetWidget()
				self.emit(SIGNAL('clientChanged(int)'), -1)
				self.tree.setCurrentItem(self.tree.topLevelItem(0))
				return

		iw = None

		if len(cesta) == 1:
			iw = InfoWidgets.clientInfoWidget(connection)
		elif len(cesta) == 2:
			pol = cesta[1]
			typ = pol.data(0, Qt.UserRole).toString()
			if typ == 'cpu':
				iw = InfoWidgets.cpuInfoWidget(connection)
			elif typ == 'projects':
				iw = InfoWidgets.projectsInfoWidget(connection)
			elif typ == 'statistics':
				iw = InfoWidgets.statisticsInfoWidget(connection)
			elif typ == 'filetransfers':
				iw = InfoWidgets.filetransfersInfoWidget(connection)
			elif typ == 'project':
				iw = InfoWidgets.projectInfoWidget(connection, pol)
		elif len(cesta) == 3:
			typ = cesta[1].data(0, Qt.UserRole).toString()
			if typ == "project":
				pol = cesta[2]
				if pol.data(0, Qt.UserRole).toString() == 'workunit':
					iw = InfoWidgets.workunitInfoWidget(connection, cesta[1], cesta[2])

		if iw is None:
			self.infoWidget.unsetWidget()
		else:
			self.connect(iw, SIGNAL("showStatusBarMsg(QString)"), self.emitStatusBarMsg)
			self.infoWidget.setWidget(iw)

