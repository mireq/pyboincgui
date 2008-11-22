from PyQt4.QtGui import QWidget, QLabel, QGridLayout, QVBoxLayout, QHBoxLayout, QGroupBox, QScrollArea
from PyQt4.QtCore import Qt, SIGNAL, QString
from BoincGui.titleframe import titleFrame
from infoWidget import infoWidget
from Boinc.interface import Interface

class clientInfoWidget(infoWidget):
	def __init__(self, client, parent = None):
		infoWidget.__init__(self, client, parent)
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
				self.connect(self.__client, SIGNAL('projectState(PyQt_PyObject)'), self.__newClientState)
				self.__client.getState()

	def __newClientState(self, state):
		# odstranime vsetkych potomkov
		self.disconnect(self.__client, SIGNAL('projectState(PyQt_PyObject)'), self.__newClientState)
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
