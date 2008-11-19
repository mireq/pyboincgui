from infoWidget import infoWidget
from PyQt4.QtCore import Qt, SIGNAL, QVariant
from PyQt4.QtGui import QColor, QHBoxLayout, QListWidget, QListWidgetItem, QVBoxLayout, QGroupBox, QRadioButton
from BoincGui.linechart import LineChartFrame

class statisticsInfoWidget(infoWidget):
	__chart = None
	__mainLayout = None
	__statistics = None
	__projectsList = None
	__buttonsLayout = None
	__statisticGroupBox = None
	__statisticLayout = None
	__modeGroupBox = None
	__modeLayout = None
	__colors = [Qt.red, QColor(200, 160, 30), Qt.darkGreen, Qt.blue, Qt.black, Qt.darkRed, Qt.darkBlue]

	def __init__(self, client, parent = None):
		infoWidget.__init__(self, parent)
		self.__mainLayout = QHBoxLayout()
		self.__chart = LineChartFrame()

		self.__projectsList = QListWidget()
		self.__projectsList.setFixedWidth(200)

		self.__statisticGroupBox = QGroupBox(self.tr("Statistics type"))
		self.__statisticLayout = QVBoxLayout()
		self.__statisticGroupBox.setLayout(self.__statisticLayout)

		userTotalRadio   = QRadioButton(self.tr("User total"), self.__statisticGroupBox)
		userAverageRadio = QRadioButton(self.tr("User average"), self.__statisticGroupBox)
		hostTotalRadio   = QRadioButton(self.tr("Host total"), self.__statisticGroupBox)
		hostAverageRadio = QRadioButton(self.tr("Host average"), self.__statisticGroupBox)

		self.__statisticLayout.addWidget(userTotalRadio)
		self.__statisticLayout.addWidget(userAverageRadio)
		self.__statisticLayout.addWidget(hostTotalRadio)
		self.__statisticLayout.addWidget(hostAverageRadio)

		self.__buttonsLayout = QVBoxLayout()
		self.__buttonsLayout.addWidget(self.__projectsList)
		self.__buttonsLayout.addWidget(self.__statisticGroupBox)

		self.__mainLayout.addWidget(self.__chart)
		self.__mainLayout.addLayout(self.__buttonsLayout)
		self.setMainLayout(self.__mainLayout)

		userTotalRadio.setChecked(True)
		self.connect(userTotalRadio, SIGNAL("toggled(bool)"), self.__setUserTotalGraph)
		self.connect(userAverageRadio, SIGNAL("toggled(bool)"), self.__setUserAverageGraph)
		self.connect(hostTotalRadio, SIGNAL("toggled(bool)"), self.__setHostTotalGraph)
		self.connect(hostAverageRadio, SIGNAL("toggled(bool)"), self.__setHostAverageGraph)

		self.connect(self.__projectsList, SIGNAL("itemChanged(QListWidgetItem *)"), self.__updateStatisticsGraph)
		self.connect(client, SIGNAL("getStatisticsRecv(PyQt_PyObject)"), self.__updateStatistics)
		client.getStatistics()

	def __setUserTotalGraph(self, checked):
		if checked:
			self.__chart.setIndex(0)

	def __setUserAverageGraph(self, checked):
		if checked:
			self.__chart.setIndex(1)

	def __setHostTotalGraph(self, checked):
		if checked:
			self.__chart.setIndex(2)

	def __setHostAverageGraph(self, checked):
		if checked:
			self.__chart.setIndex(3)

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
