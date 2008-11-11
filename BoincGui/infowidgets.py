# -*- coding: UTF-8 -*-
from PyQt4.QtGui import QWidget, QLabel, QGridLayout, QVBoxLayout, QHBoxLayout, QScrollArea, QFrame, QGroupBox, QColor, QTabWidget, QTableWidget, QHeaderView, QTableWidgetItem, QToolButton, QMenu, QAction
from PyQt4.QtCore import QString, Qt, SIGNAL
from titleframe import titleFrame
from Boinc.interface import Interface
from piechart import PieChartFrame
from os import execlp, fork
from platform import system
import os

class urlAction(QAction):
	__url = ""
	def __init__(self, url, name, description, parent):
		QAction.__init__(self, name, parent)
		self.setToolTip(description)
		self.setStatusTip(description)
		self.__url = url
		self.connect(self, SIGNAL("triggered()"), self.openUrl)

	def openUrl(self):
		pid = fork()
		if pid == 0:
			s = system()
			if os.name == 'mac':
				execlp('open', 'open', self.__url)
			if s == "Windows":
				execlp('start', 'start', self.__url)
			else:
				execlp('xdg-open', 'xdg-open', self.__url)

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
			self.__title.deleteLater()

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
			projects = self.__client.projectState()
			if not projects is None:
				self.__newClientState(projects)
			else:
				self.connect(self.__client, SIGNAL('getStateRecv(PyQt_PyObject)'), self.__newClientState)
				self.__client.getState()

	def __newClientState(self, state):
		# odstranime vsetkych potomkov
		self.disconnect(self.__client, SIGNAL('getStateRecv(PyQt_PyObject)'), self.__newClientState)
		potomok = self.__advClientInfoLayout.takeAt(0)
		while not potomok is None:
			#self.__advClientInfoLayout.removeWidget(potomok)
			del(potomok)
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
		#self.__client.bInterface().get_state(self.__changeState)

		projects = self.__client.projectState()
		if not projects is None:
			self.__updateClientState(projects)
		else:
			self.connect(self.__client, SIGNAL('getStateRecv(PyQt_PyObject)'), self.__updateClientState)
			self.__client.getState()


	def __updateClientState(self, state):
		self.disconnect(self.__client, SIGNAL('getStateRecv(PyQt_PyObject)'), self.__updateClientState)
		self.__vendorLabel.setText(state['host_info']['p_vendor'])
		self.__modelLabel.setText(state['host_info']['p_model'])
		self.__ncpusLabel.setText(state['host_info']['p_ncpus'])
		self.__featuresLabel.setText(state['host_info']['p_features'])


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

		self.__tabWidget.addTab(self.__table, self.tr("&Projects"))
		self.__tabWidget.addTab(self.__chart, self.tr("&Resources Share"))

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

class projectInfoWidget(infoWidget):
	__master_url = ""
	__projectCached = None

	__mainLayout = None

	__projectInfo = None
	__projectInfoLayout = None
	__projectLinks = None

	#informacie o projekte
	__masterUrlLabel       = None
	__masterUrlText        = None
	__projectNameLabel     = None
	__projectNameText      = None
	__userNameLabel        = None
	__userNameText         = None
	__teamNameLabel        = None
	__teamNameText         = None
	__userTotalCreditLabel = None
	__userTotalCreditText  = None
	__hostTotalCreditLabel = None
	__hostTotalCreditText  = None

	__projectLinksButton = None
	__projectLinksMenu   = None

	def __init__(self, client, project, parent = None):
		infoWidget.__init__(self, parent)

		self.__mainLayout = QGridLayout()
		self.__mainLayout.setRowStretch(1, 1)
		self.setMainLayout(self.__mainLayout)

		self.__projectInfo = QGroupBox(self.tr("Project Info"));
		self.__projectInfoLayout = QGridLayout()
		self.__projectInfo.setLayout(self.__projectInfoLayout)

		self.__projectLinks = QHBoxLayout()
		self.__projectLinksButton = QToolButton()
		self.__projectLinksButton.setText(self.tr("Project Links"))
		self.__projectLinksButton.hide()
		self.__projectLinks.addWidget(self.__projectLinksButton)
		self.__projectLinks.addStretch(1)

		self.__mainLayout.addWidget(self.__projectInfo, 0, 0)
		self.__mainLayout.addLayout(self.__projectLinks, 2, 0)

		self.__masterUrlLabel       = QLabel(self.tr("Master URL"))
		self.__projectNameLabel     = QLabel(self.tr("Project Name"))
		self.__userNameLabel        = QLabel(self.tr("User Name"))
		self.__teamNameLabel        = QLabel(self.tr("Team Name"))
		self.__userTotalCreditLabel = QLabel(self.tr("Total User Credits"))
		self.__hostTotalCreditLabel = QLabel(self.tr("Total Host Credits"))

		self.__masterUrlText       = QLabel()
		self.__projectNameText     = QLabel()
		self.__userNameText        = QLabel()
		self.__teamNameText        = QLabel()
		self.__userTotalCreditText = QLabel()
		self.__hostTotalCreditText = QLabel()

		self.__masterUrlText.setTextFormat(Qt.PlainText)
		self.__projectNameText.setTextFormat(Qt.PlainText)
		self.__userNameText.setTextFormat(Qt.PlainText)
		self.__teamNameText.setTextFormat(Qt.PlainText)
		self.__userTotalCreditText.setTextFormat(Qt.PlainText)
		self.__hostTotalCreditText.setTextFormat(Qt.PlainText)

		self.__masterUrlLabel.hide()
		self.__projectNameLabel.hide()
		self.__userNameLabel.hide()
		self.__teamNameLabel.hide()
		self.__userTotalCreditLabel.hide()
		self.__hostTotalCreditLabel.hide()

		self.__masterUrlText.hide()
		self.__projectNameText.hide()
		self.__userNameText.hide()
		self.__teamNameText.hide()
		self.__userTotalCreditText.hide()
		self.__hostTotalCreditText.hide()

		self.__projectInfoLayout.addWidget(self.__masterUrlLabel,        0, 0)
		self.__projectInfoLayout.addWidget(self.__projectNameLabel,      1, 0)
		self.__projectInfoLayout.addWidget(self.__userNameLabel,         2, 0)
		self.__projectInfoLayout.addWidget(self.__teamNameLabel,         3, 0)
		self.__projectInfoLayout.addWidget(self.__userTotalCreditLabel, 4, 0)
		self.__projectInfoLayout.addWidget(self.__hostTotalCreditLabel, 5, 0)

		self.__projectInfoLayout.addWidget(self.__masterUrlText,        0, 1)
		self.__projectInfoLayout.addWidget(self.__projectNameText,      1, 1)
		self.__projectInfoLayout.addWidget(self.__userNameText,         2, 1)
		self.__projectInfoLayout.addWidget(self.__teamNameText,         3, 1)
		self.__projectInfoLayout.addWidget(self.__userTotalCreditText, 4, 1)
		self.__projectInfoLayout.addWidget(self.__hostTotalCreditText, 5, 1)

		self.__master_url = project.data(0, Qt.UserRole).toString()
		self.__projectCached = None

		self.__projectLinksMenu = QMenu()
		self.__projectLinksButton.setPopupMode(QToolButton.InstantPopup)
		self.__projectLinksButton.setMenu(self.__projectLinksMenu)

		projects = client.projectState()
		if not projects is None:
			self.updateProjects(projects)
		self.connect(client, SIGNAL("projectState(PyQt_PyObject)"), self.updateProjects)



	def __changeLabels(self, project, key, label, text):
		try:
			inf = project[key]
			if type(inf) == type(u""):
				text.setText(inf)
				text.show()
				label.show()
		except KeyError:
			text.hide()
			label.hide()

	def updateProjects(self, projects):
		projects = projects['project']
		project = None

		for proj in projects:
			if proj['master_url'] == self.__master_url:
				project = proj
				break

		# ak sme nenasli projekt
		if project is None:
			return

		if project != self.__projectCached:
			self.__projectCached = project
			try:
				self.setTitle(titleFrame(project['project_name']))
			except KeyError:
				pass

			self.__changeLabels(project, 'master_url', self.__masterUrlLabel, self.__masterUrlText)
			self.__changeLabels(project, 'project_name', self.__projectNameLabel, self.__projectNameText)
			self.__changeLabels(project, 'user_name', self.__userNameLabel, self.__userNameText)
			self.__changeLabels(project, 'team_name', self.__teamNameLabel, self.__teamNameText)
			self.__changeLabels(project, 'user_total_credit', self.__userTotalCreditLabel, self.__userTotalCreditText)
			self.__changeLabels(project, 'host_total_credit', self.__hostTotalCreditLabel, self.__hostTotalCreditText)

			try:
				self.__projectLinksMenu.clear()
				guiUrls = project['gui_urls']['gui_url']

				if type(guiUrls) == type({}):
					self.__projectLinksMenu.addAction(urlAction(guiUrls['url'], guiUrls['name'], guiUrls['description'], self.__projectLinksMenu))
				else:
					for url in guiUrls:
						self.__projectLinksMenu.addAction(urlAction(url['url'], url['name'], url['description'], self.__projectLinksMenu))

				try:
					ifTeamUrls = project['gui_urls']['ifteam']['gui_url']
					self.__projectLinksMenu.addSeparator()
					if type(ifTeamUrls) == type({}):
						self.__projectLinksMenu.addAction(urlAction(ifTeamUrls['url'], ifTeamUrls['name'], ifTeamUrls['description'], self.__projectLinksMenu))
					else:
						for url in ifTeamUrls:
							self.__projectLinksMenu.addAction(urlAction(url['url'], url['name'], url['description'], self.__projectLinksMenu))
				except KeyError, msg:
					pass
				self.__projectLinksButton.show()
			except KeyError:
				self.__projectLinksButton.hide()


