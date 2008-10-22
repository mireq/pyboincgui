from PyQt4.QtGui import QWidget, QHBoxLayout, QTableView, QTreeView
from PyQt4.QtCore import QSize
from clienttree import clientTreeView, clientTreeModel

class mainWidget(QWidget):
	def __init__(self, parent = None):
		QWidget.__init__(self, parent)
		self.layout = QHBoxLayout()
		self.setLayout(self.layout)

		self.tree = clientTreeView()
		self.tree.setIconSize(QSize(64, 64))
		self.model = clientTreeModel(self)
		self.tree.setModel(self.model)

		self.layout.addWidget(self.tree)