from infoWidget import infoWidget
from PyQt4.QtCore import Qt, SIGNAL
from PyQt4.QtGui import QColor, QVBoxLayout
from BoincGui.linechart import LineChartFrame

class statisticsInfoWidget(infoWidget):
	__chart = None
	__mainLayout = None
	__statistics = None
	__colors = [Qt.red, Qt.yellow, Qt.green, Qt.blue, Qt.black, Qt.darkRed, Qt.darkGreen, Qt.darkBlue]

	def __init__(self, client, parent = None):
		infoWidget.__init__(self, parent)
		self.__mainLayout = QVBoxLayout()
		self.__chart = LineChartFrame()
		self.__mainLayout.addWidget(self.__chart)
		self.setMainLayout(self.__mainLayout)
		self.connect(client, SIGNAL("getStatisticsRecv(PyQt_PyObject)"), self.__updateStatistics)
		client.getStatistics()

	def __updateStatistics(self, statistics):
		self.__statistics = statistics
		self.__updateStatisticsGraph()

	def __updateStatisticsGraph(self):
		i = 0
		for key in self.__statistics.keys():
			name = self.sender().getProjectName(key)
			if name is None:
				name = key
			self.__chart.addGraph(self.__statistics[key], name, self.__colors[i])
			i = i + 1
			if i >= len(self.__colors):
				i = 0
