from infoWidget import infoWidget
from PyQt4.QtCore import Qt, SIGNAL
from PyQt4.QtGui import QColor, QTabWidget, QTableWidgetItem, QTableWidget, QVBoxLayout, QHeaderView
from BoincGui.piechart import PieChartFrame

class projectsInfoWidget(infoWidget):
	__mainLayout = None
	__tabWidget = None
	__chart = None
	__table = None
	__colors = [Qt.red, QColor(120, 160, 215), Qt.yellow, Qt.green, QColor(250, 125, 30), Qt.blue]
	__angles = []

	def __init__(self, client, parent = None):
		infoWidget.__init__(self, parent)
		self.__angles = []

		self.__tabWidget = QTabWidget()
		self.__mainLayout = QVBoxLayout()
		self.__mainLayout.addWidget(self.__tabWidget)
		self.setMainLayout(self.__mainLayout, False)

		self.__chart = PieChartFrame()
		self.__table = QTableWidget()
		self.__table.verticalHeader().hide()
		self.__table.setColumnCount(3)
		hh = self.__table.horizontalHeader()
		hh.setResizeMode(QHeaderView.Stretch)
		#self.__table.setHeaderData(0, Qt.Horizonatal, QVariant(self.tr("Project Name")), Qt.DiaplayRole)
		self.__table.setHorizontalHeaderItem(0, QTableWidgetItem(self.tr("Project Name")))
		self.__table.setHorizontalHeaderItem(1, QTableWidgetItem(self.tr("Project URL")))
		self.__table.setHorizontalHeaderItem(2, QTableWidgetItem(self.tr("Resource Share")))

		self.__tabWidget.addTab(self.__chart, self.tr("&Resources Share"))
		self.__tabWidget.addTab(self.__table, self.tr("&Projects"))

		projects = client.projectState()
		if not projects is None:
			self.updateProjects(projects)
		self.connect(client, SIGNAL("projectState(PyQt_PyObject)"), self.updateProjects)

	def updateProjects(self, projects):
		projects = projects['project']
		#self.__chart.removeItems()
		update = False
		i = 0
		full = 0.0
		for projekt in projects:
			full = full + float(projekt['resource_share'])
	
		for i in range(len(projects)):
			projekt = projects[i]
			angle = int(360.0 * 16.0 * (float(projekt['resource_share']) / full))
			try:
				if angle != self.__angles[i]:
					update = True
					self.__angles[i] = angle
			except IndexError:
				update = True
				self.__angles.append(angle)

		self.__angles = self.__angles[0:len(projects)]
		if update:
			self.__chart.removeItems()
			self.__table.setRowCount(len(projects))
			for i in range(len(projects)):
				#aktualizujeme tabulku
				projectItem = QTableWidgetItem(projekt['project_name'])
				projectItem.setFlags(Qt.ItemIsEnabled|Qt.ItemIsSelectable)
				urlItem = QTableWidgetItem(projekt['master_url'])
				urlItem.setFlags(Qt.ItemIsEnabled|Qt.ItemIsSelectable)
				shareItem = QTableWidgetItem(str(round(float(projekt['resource_share']))))
				shareItem.setFlags(Qt.ItemIsEnabled|Qt.ItemIsSelectable)

				self.__table.setItem(i, 0, projectItem)
				self.__table.setItem(i, 1, urlItem)
				self.__table.setItem(i, 2, shareItem)
		
				#aktualizujeme graf
				projekt = projects[i]
				angle = int(360.0 * 16.0 * (float(projekt['resource_share']) / full))
				self.__chart.addItem(angle, projekt['project_name'], self.__colors[i])
				i = i + 1
				if i >= len(self.__colors):
					i = 0
