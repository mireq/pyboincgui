# -*- coding: UTF-8 -*-
from PyQt4.QtGui import QWidget, QLabel, QGridLayout, QVBoxLayout, QScrollArea, QFrame, QGroupBox, QColor
from PyQt4.QtCore import QString, Qt, SIGNAL
from titleframe import titleFrame
from Boinc.interface import Interface
from piechart import PieChartFrame

class infoWidget(QWidget):

	__mainLayout = None
	__connLayout = None
	__title  = None
	__layout = None

	__scrollArea   = None
	__scrollWidget = None

	__connGroupBox = None

	__advClientInfoLayout   = None
	__advClientInfoGroupBox = None

	def __init__(self, parent = None):
		QWidget.__init__(self, parent)
		self.__mainLayout = QVBoxLayout(self)

	def setMainLayout(self, layout, scroll = True):
		if not self.__layout is None:
			self.__mainLayout.removeItem(self.__layout)
		if not self.__scrollArea is None:
			self.__mainLayout.removeWidget(self.__scrollArea)

		self.__layout = None
		self.__scrollArea   = None
		self.__scrollWidget = None

		if not layout is None:
			if scroll:
				self.__scrollWidget = QWidget()
				self.__scrollWidget.setLayout(layout)

				self.__scrollArea = QScrollArea()
				self.__scrollArea.setWidgetResizable(True)
				self.__scrollArea.setWidget(self.__scrollWidget)
				self.__scrollArea.setFrameStyle(QFrame.NoFrame)
				self.__scrollArea.setFrameShadow(QFrame.Plain)

				self.__mainLayout.addWidget(self.__scrollArea)

			else:
				self.__mainLayout.addLayout(layout)
			self.__layout = layout
		else:
			self.__layout = layout

	def setTitle(self, title):
		if not self.__title is None:
			self.__mainLayout.removeWidget(self.__title)

		if not title is None:
			self.__mainLayout.insertWidget(0, title)
		self.__title = title;

class clientInfoWidget(infoWidget):
	def __init__(self, client, parent = None):
		infoWidget.__init__(self, parent)
		self.__client = client;
		#self.setLayout(self.__mainLayout)

		hostStr = client.host()
		portStr = str(client.port())
		localStr = ""
		if client.local():
			localStr = self.tr("Yes")
		else:
			localStr = self.tr("No")

		self.__hostLabel  = QLabel(self.tr("Host:"))
		self.__portLabel  = QLabel(self.tr("Port:"))
		self.__localLabel = QLabel(self.tr("Local client:"))
		self.__stateLabel = QLabel(self.tr("Client state:"))

		self.__hostLabelInf  = QLabel()
		self.__portLabelInf  = QLabel()
		self.__localLabelInf = QLabel()
		self.__stateLabelInf = QLabel()

		self.__hostLabelInf.setTextFormat(Qt.PlainText)
		self.__portLabelInf.setTextFormat(Qt.PlainText)
		self.__localLabelInf.setTextFormat(Qt.PlainText)
		self.__stateLabelInf.setTextFormat(Qt.PlainText)

		self.__hostLabelInf.setWordWrap(True)
		self.__portLabelInf.setWordWrap(True)
		self.__localLabelInf.setWordWrap(True)
		self.__stateLabelInf.setWordWrap(True)

		self.__hostLabelInf.setText(hostStr)
		self.__portLabelInf.setText(portStr)
		self.__localLabelInf.setText(localStr)

		self.__connLayout = QGridLayout()
		self.__connLayout.addWidget(self.__hostLabel, 0, 0)
		self.__connLayout.addWidget(self.__hostLabelInf, 0, 1)
		self.__connLayout.addWidget(self.__portLabel, 1, 0)
		self.__connLayout.addWidget(self.__portLabelInf, 1, 1)
		self.__connLayout.addWidget(self.__localLabel, 2, 0)
		self.__connLayout.addWidget(self.__localLabelInf, 2, 1)
		self.__connLayout.addWidget(self.__stateLabel, 3, 0)
		self.__connLayout.addWidget(self.__stateLabelInf, 3, 1)

		self.__connGroupBox = QGroupBox(self.tr("Connection details"))
		self.__connGroupBox.setLayout(self.__connLayout)

		self.__advClientInfoGroupBox = QGroupBox(self.tr("Client Details"))
		self.__advClientInfoLayout   = QGridLayout();
		self.__advClientInfoGroupBox.setLayout(self.__advClientInfoLayout)

		self.setTitle(titleFrame(self.tr("Informamtions about Client")))
		self.__mainLayout = QVBoxLayout()
		self.__mainLayout.addWidget(self.__connGroupBox)
		self.__mainLayout.addWidget(self.__advClientInfoGroupBox)
		self.__mainLayout.addStretch(1)
		self.setMainLayout(self.__mainLayout)

		self.connect(client, SIGNAL("connectStateChanged(int)"), self.__connectStateChanged)
		self.connect(self, SIGNAL('newClientState(PyQt_PyObject)'), self.__newClientState)
		self.__connectStateChanged()


	def __getConnStateString(self, conn):
		if conn == Interface.connected:
			return self.tr("connected")
		elif conn == Interface.connecting:
			return self.tr("connecting")
		elif conn == Interface.disconnected:
			return self.tr("disconnected")
		else:
			return self.tr("unauthorized")

	def __connectStateChanged(self):
		conn = self.__client.connected()
		str = self.__getConnStateString(conn)
		self.__stateLabelInf.setText(str)
		if conn == Interface.connected or conn == Interface.unauthorized:
			self.__client.bInterface().get_state(self.__changeState)

	def __newClientState(self, state):
		# odstranime vsetkych potomkov
		potomok = self.__advClientInfoLayout.takeAt(0)
		while not potomok is None:
			self.__advClientInfoLayout.removeWidget(potomok)
			potomok = self.__advClientInfoLayout.takeAt(0)

		self.__advClientInfoLayout.addWidget(QLabel(self.tr("Host:")), 0, 0)
		domainName = QLabel(state['host_info']['domain_name'])
		domainName.setTextFormat(Qt.PlainText)
		domainName.setWordWrap(True)
		self.__advClientInfoLayout.addWidget(domainName, 0, 1)

		self.__advClientInfoLayout.addWidget(QLabel(self.tr("OS Name:")), 1, 0)
		hostInfo = QLabel(state['host_info']['os_name'])
		hostInfo.setTextFormat(Qt.PlainText)
		hostInfo.setWordWrap(True)
		self.__advClientInfoLayout.addWidget(hostInfo, 1, 1)

		self.__advClientInfoLayout.addWidget(QLabel(self.tr("OS Version:")), 2, 0)
		osVersion = QLabel(state['host_info']['os_version'])
		osVersion.setTextFormat(Qt.PlainText)
		osVersion.setWordWrap(True)
		self.__advClientInfoLayout.addWidget(osVersion, 2, 1)

		self.__advClientInfoLayout.addWidget(QLabel(self.tr("Platform:")), 3, 0)
		platformName = QLabel(state['platform_name'])
		platformName.setTextFormat(Qt.PlainText)
		platformName.setWordWrap(True)
		self.__advClientInfoLayout.addWidget(platformName, 3, 1)

		self.__advClientInfoLayout.addWidget(QLabel(self.tr("Client Version:")), 4, 0)
		clientStr = QString("%1.%2.%3").arg(state['core_client_major_version']).arg(state['core_client_minor_version']).arg(state['core_client_release'])
		clientVersion = QLabel(clientStr)
		clientVersion.setTextFormat(Qt.PlainText)
		clientVersion.setWordWrap(True)
		self.__advClientInfoLayout.addWidget(clientVersion, 4, 1)

	def __changeState(self, state):
		self.emit(SIGNAL("newClientState(PyQt_PyObject)"), state)

class cpuInfoWidget(infoWidget):
	__client = None
	__mainLayout = None

	__vendorLabel   = None
	__modelLabel    = None
	__ncpusLabel    = None
	__featuresLabel = None

	def __init__(self, client, parent = None):
		infoWidget.__init__(self, parent)
		self.__client = client

		self.__mainLayout = QGridLayout();

		self.__vendorLabel   = QLabel()
		self.__modelLabel    = QLabel()
		self.__ncpusLabel    = QLabel()
		self.__featuresLabel = QLabel()

		self.__vendorLabel.setTextFormat(Qt.PlainText)
		self.__modelLabel.setTextFormat(Qt.PlainText)
		self.__ncpusLabel.setTextFormat(Qt.PlainText)
		self.__featuresLabel.setTextFormat(Qt.PlainText)

		self.__vendorLabel.setWordWrap(True)
		self.__modelLabel.setWordWrap(True)
		self.__ncpusLabel.setWordWrap(True)
		self.__featuresLabel.setWordWrap(True)

		self.__mainLayout.addWidget(QLabel(self.tr("Vendor: ")), 0, 0, Qt.AlignTop)
		self.__mainLayout.addWidget(self.__vendorLabel, 0, 1, Qt.AlignTop)
		self.__mainLayout.addWidget(QLabel(self.tr("Model: ")), 1, 0, Qt.AlignTop)
		self.__mainLayout.addWidget(self.__modelLabel, 1, 1, Qt.AlignTop)
		self.__mainLayout.addWidget(QLabel(self.tr("Number of CPUs:")), 2, 0, Qt.AlignTop)
		self.__mainLayout.addWidget(self.__ncpusLabel, 2, 1, Qt.AlignTop)
		self.__mainLayout.addWidget(QLabel(self.tr("Features: ")), 3, 0, Qt.AlignTop)
		self.__mainLayout.addWidget(self.__featuresLabel, 3, 1, Qt.AlignTop)
		self.__mainLayout.setColumnStretch(1, 1)
		self.__mainLayout.setRowStretch(4, 1)

		self.setTitle(titleFrame(self.tr("CPU Info")))
		self.setMainLayout(self.__mainLayout)
		self.connect(self, SIGNAL('newClientState(PyQt_PyObject)'), self.__updateClientState)
		self.__client.bInterface().get_state(self.__changeState)

	def __updateClientState(self, state):
		self.__vendorLabel.setText(state['host_info']['p_vendor'])
		self.__modelLabel.setText(state['host_info']['p_model'])
		self.__ncpusLabel.setText(state['host_info']['p_ncpus'])
		self.__featuresLabel.setText(state['host_info']['p_features'])

	def __changeState(self, state):
		self.emit(SIGNAL("newClientState(PyQt_PyObject)"), state)

class projectsInfoWidget(infoWidget):
	__mainLayout = None
	__chart = None
	__colors = [Qt.red, QColor(120, 160, 215), Qt.yellow, Qt.green, QColor(250, 125, 30), Qt.blue]

	def __init__(self, client, parent = None):
		infoWidget.__init__(self, parent)
		self.__chart = PieChartFrame()
		self.__mainLayout = QVBoxLayout()
		self.__mainLayout.addWidget(self.__chart)
		self.setMainLayout(self.__mainLayout, False)

		projects = client.projectStatus()
		if not projects is None:
			self.updateProjects(projects)
		self.connect(client, SIGNAL("projectStatus(PyQt_PyObject)"), self.updateProjects)

	def updateProjects(self, projects):
		self.__chart.removeItems()
		i = 0
		full = 0.0
		for projekt in projects:
			full = full + float(projekt['resource_share'])
	
		for projekt in projects:
			self.__chart.addItem(360.0 * 16.0 * (float(projekt['resource_share']) / full), projekt['project_name'], self.__colors[i])
			i = i + 1
			if i >= len(self.__colors):
				i = 0