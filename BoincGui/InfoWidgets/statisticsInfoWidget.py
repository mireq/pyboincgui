from infoWidget import infoWidget
from PyQt4.QtCore import Qt, SIGNAL, QVariant
from PyQt4.QtGui import QColor, QHBoxLayout, QListWidget, QListWidgetItem
from BoincGui.linechart import LineChartFrame

class statisticsInfoWidget(infoWidget):
	__chart = None
	__mainLayout = None
	__statistics = None
	__projectsList = None
	__colors = [Qt.red, Qt.yellow, Qt.green, Qt.blue, Qt.black, Qt.darkRed, Qt.darkGreen, Qt.darkBlue]

	def __init__(self, client, parent = None):
		infoWidget.__init__(self, parent)
		self.__mainLayout = QHBoxLayout()
		self.__chart = LineChartFrame()
		self.__projectsList = QListWidget()
		self.__projectsList.setFixedWidth(200)
		self.__mainLayout.addWidget(self.__chart)
		self.__mainLayout.addWidget(self.__projectsList)
		self.setMainLayout(self.__mainLayout)
		self.connect(self.__projectsList, SIGNAL("itemChanged(QListWidgetItem *)"), self.__updateStatisticsGraph)
		self.connect(client, SIGNAL("getStatisticsRecv(PyQt_PyObject)"), self.__updateStatistics)
		client.getStatistics()

	def __updateStatistics(self, statistics):
		self.disconnect(self.sender(), SIGNAL("getStatisticsRecv(PyQt_PyObject)"), self.__updateStatistics)
		self.__statistics = statistics
		self.__addListItems()
		self.__updateStatisticsGraph()

	def __addListItems(self):
		i = 0
		for key in self.__statistics.keys():
			name = self.sender().getProjectName(key)
			if name is None:
				name = key
			color = self.__colors[i]

			item = QListWidgetItem(name)
			item.setData(Qt.DecorationRole, QVariant(QColor(color)))
			item.setData(Qt.UserRole, QVariant(key))
			item.setFlags(Qt.ItemIsSelectable|Qt.ItemIsUserCheckable|Qt.ItemIsEnabled)
			item.setCheckState(Qt.Checked)
			self.__projectsList.addItem(item)

			i = i + 1
			if i >= len(self.__colors):
				i = 0

	def __updateStatisticsGraph(self):
		self.__chart.removeGraphs()
		for i in range(self.__projectsList.count()):
			item = self.__projectsList.item(i)
			color = item.data(Qt.DecorationRole)
			name = str(item.data(Qt.DisplayRole).toString())
			key = str(item.data(Qt.UserRole).toString())
			if item.checkState() == Qt.Checked:
				self.__chart.addGraph(self.__statistics[key], name, color)
		#i = 0
		#for key in self.__statistics.keys():
			#name = self.sender().getProjectName(key)
			#if name is None:
				#name = key
			#self.__chart.addGraph(self.__statistics[key], name, self.__colors[i])
			#i = i + 1
			#if i >= len(self.__colors):
				#i = 0
