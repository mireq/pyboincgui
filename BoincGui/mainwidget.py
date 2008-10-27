from PyQt4.QtGui import QWidget, QHBoxLayout, QTableView, QTreeView, QStackedWidget, QLabel
from PyQt4.QtCore import QSize, SIGNAL
from clienttree import clientTreeWidget

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
		self.layout = QHBoxLayout()
		self.setLayout(self.layout)

		self.tree = clientTreeWidget(connManager)
		self.infoWidget = infoStackWidget()

		self.layout.addWidget(self.tree)
		self.layout.addWidget(self.infoWidget)

		self.connect(self.tree, SIGNAL("currentItemChanged(QTreeWidgetItem *, QTreeWidgetItem *)"), self.changeActive)

	def changeActive(self, prev, next):
		self.infoWidget.setWidget(QLabel("ok"))