from PyQt4.QtGui import QWidget, QHBoxLayout, QTableView, QTreeView, QStackedWidget, QLabel
from PyQt4.QtCore import QSize, SIGNAL, Qt
from clienttree import clientTreeWidget
import infowidgets

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
		self.currentWidget = None

class mainWidget(QWidget):
	def __init__(self, connManager, parent = None):
		QWidget.__init__(self, parent)
		self.__connManager = connManager
		self.layout = QHBoxLayout()
		self.setLayout(self.layout)

		self.tree = clientTreeWidget(connManager)
		self.infoWidget = infoStackWidget()

		self.layout.addWidget(self.tree)
		self.layout.addWidget(self.infoWidget)

		self.connect(self.tree, SIGNAL("currentItemChanged(QTreeWidgetItem *, QTreeWidgetItem *)"), self.changeActive)

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
			connection = self.__connManager.getConnection(index)
			self.emit(SIGNAL('clientChanged(int)'), index)
			if connection is None:
				self.infoWidget.unsetWidget()
				self.tree.setCurrentItem(self.tree.topLevelItem(0))
				self.emit(SIGNAL('clientChanged(int)'), -1)
				return

		if len(cesta) == 1:
			self.infoWidget.setWidget(infowidgets.clientInfoWidget(connection))
		elif len(cesta) == 2:
			pol = cesta[1]
			typ = pol.data(0, Qt.UserRole).toString()
			if typ == 'cpu':
				self.infoWidget.setWidget(infowidgets.cpuInfoWidget(connection))
			elif typ == 'projects':
				self.infoWidget.setWidget(infowidgets.projectsInfoWidget(connection))
		elif len(cesta) == 3:
			pol = cesta[1]
			typ = pol.data(0, Qt.UserRole).toString()
			if typ == 'projects':
				self.infoWidget.setWidget(QLabel(cesta[2].data(0, Qt.UserRole).toString()))
