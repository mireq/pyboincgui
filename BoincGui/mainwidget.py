from PyQt4.QtGui import QWidget, QHBoxLayout, QTableView, QTreeView
from PyQt4.QtCore import QSize, SIGNAL
from clienttree import clientTreeWidget

class mainWidget(QWidget):
	def __init__(self, connManager, parent = None):
		QWidget.__init__(self, parent)
		self.layout = QHBoxLayout()
		self.setLayout(self.layout)

		self.tree = clientTreeWidget(connManager)
		#self.model = clientTreeModel(connManager, self)
		#self.tree.setModel(self.model)

		self.layout.addWidget(self.tree)