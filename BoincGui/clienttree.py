from PyQt4.QtGui import QTreeView, QPixmap, QIcon
from PyQt4.QtCore import QAbstractItemModel, QModelIndex, QVariant, Qt

class clientTreeView(QTreeView):
	pass

class clientItem:
	__childNodes = []
	def __init__(self, parent, row):
		self.__parent = parent
		self.__row = row
	def parent(self):
		return self.__parent
	def row(self):
		return self.__row
	def childNodes(self):
		return self.__childNodes
	def name(self):
		return "podradeny"

class client:
	__childNodes = []
	def __init__(self, row):
		self.__childNodes = [clientItem(self, 0), clientItem(self, 1)]
		self.__row = row
		pass
	def parent(self):
		return None
	def name(self):
		return "nadradeny"
	def childNodes(self):
		return self.__childNodes
	def row(self):
		return self.__row

class clientTreeModel(QAbstractItemModel):
	def __init__(self, parent = None):
		QAbstractItemModel.__init__(self, parent)
		self.clients = [client(0), client(1), client(2)]

	def columnCount(self, parent = QModelIndex()):
		return 1

	def headerData(self, section, orientation, role = Qt.DisplayRole):
		if role == Qt.DisplayRole:
			return QVariant("ok")
		return QVariant()

	def data(self, index, role = Qt.DisplayRole):
		if role == Qt.DisplayRole:
			return QVariant(index.internalPointer().name())
		else:
			return QVariant()
		pass


	def index(self, row, column, parent = QModelIndex()):
		if not parent.isValid():
			return self.createIndex(row, column, self.clients[row])
		return self.createIndex(row, column, parent.internalPointer().childNodes()[row])


	def parent(self, index):
		parent = index.internalPointer().parent()
		if parent is None:
			return QModelIndex()
		else:
			return self.createIndex(parent.row(), 0, parent)


	def rowCount(self, parent = QModelIndex()):
		if not parent.isValid():
			return len(self.clients)
		else:
			ptr = parent.internalPointer()
			return len(parent.internalPointer().childNodes())
