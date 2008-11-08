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
		index = self.tree.indexOfTopLevelItem(next)
		if not index == -1:
			if next.data(0, Qt.UserRole).toInt()[0] == clientTreeWidget.Client:
				connection = self.__connManager.getConnection(index)
				self.infoWidget.setWidget(infowidgets.clientInfoWidget(connection))
			else:
				self.infoWidget.unsetWidget()
		else:
			# druha uroven
			if not self.tree.indexFromItem(next).parent().parent().isValid():
				typ = next.data(0, Qt.UserRole).toString()
				index = self.tree.indexFromItem(next).parent().row()
				connection = self.__connManager.getConnection(index)
				if typ == "cpu":
					self.infoWidget.setWidget(infowidgets.cpuInfoWidget(connection))