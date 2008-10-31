from PyQt4.QtGui import QWidget, QLabel, QGridLayout
from PyQt4.QtCore import QString, Qt, SIGNAL
from headerframe import headerFrame
from Boinc.interface import Interface

class clientInfoWidget(QWidget):
	def __init__(self, client, parent = None):
		QWidget.__init__(self, parent)
		self.__client = client;
		self.__mainLayout = QGridLayout()
		self.setLayout(self.__mainLayout)

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

		self.__hostLabelInf  = QLabel(hostStr)
		self.__portLabelInf  = QLabel(portStr)
		self.__localLabelInf = QLabel(localStr)
		self.__stateLabelInf = QLabel()

		self.__mainLayout.addWidget(headerFrame("Informacie o klientovi"), 0, 0, 1, 2)
		self.__mainLayout.addWidget(self.__hostLabel, 1, 0)
		self.__mainLayout.addWidget(self.__hostLabelInf, 1, 1)
		self.__mainLayout.addWidget(self.__portLabel, 2, 0)
		self.__mainLayout.addWidget(self.__portLabelInf, 2, 1)
		self.__mainLayout.addWidget(self.__localLabel, 3, 0)
		self.__mainLayout.addWidget(self.__localLabelInf, 3, 1)
		self.__mainLayout.addWidget(self.__stateLabel, 4, 0)
		self.__mainLayout.addWidget(self.__stateLabelInf, 4, 1)

		self.__mainLayout.setRowStretch(6, 1)

		self.connect(client, SIGNAL("connectStateChanged()"), self.__connectStateChanged)
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
		if conn == Interface.connected:
			self.__client.bInterface().get_state(self.__changeState)

	def __changeState(self, state):
		pass