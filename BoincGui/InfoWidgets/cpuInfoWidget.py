from BoincGui.titleframe import titleFrame
from infoWidget import infoWidget
from PyQt4.QtGui import QGridLayout, QLabel
from PyQt4.QtCore import Qt, SIGNAL

class cpuInfoWidget(infoWidget):
	__client = None
	__mainLayout = None

	__vendorLabel   = None
	__modelLabel    = None
	__ncpusLabel    = None
	__featuresLabel = None

	def __init__(self, client, parent = None):
		infoWidget.__init__(self, client, parent)
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
			self.connect(self.__client, SIGNAL('projectState(PyQt_PyObject)'), self.__updateClientState)
			self.__client.getState()


	def __updateClientState(self, state):
		self.disconnect(self.__client, SIGNAL('projectState(PyQt_PyObject)'), self.__updateClientState)
		self.__vendorLabel.setText(state['host_info']['p_vendor'])
		self.__modelLabel.setText(state['host_info']['p_model'])
		self.__ncpusLabel.setText(state['host_info']['p_ncpus'])
		self.__featuresLabel.setText(state['host_info']['p_features'])
