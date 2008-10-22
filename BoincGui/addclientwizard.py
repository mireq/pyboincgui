from PyQt4.QtCore import SIGNAL, SLOT, QFile, QFSFileEngine, QAbstractFileEngine, QString
from PyQt4.QtGui import QWizard, QWizardPage, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout, QRadioButton, QLineEdit, QPushButton, QFileDialog, QSpinBox, QDialog

class introPage(QWizardPage):
	def __init__(self, parent = None):
		QWizardPage.__init__(self, parent)
		self.setTitle(self.tr("Pridat klienta"))
		self.label = QLabel(self.tr("Vyberte prosim typ klienta."))
		self.label.setWordWrap(True)

		self.localRadioButton  = QRadioButton(self.tr("Lokalny klient"), self)
		self.remoteRadioButton = QRadioButton(self.tr("Vzdialeny klient"),  self)
		self.localRadioButton.setChecked(True)

		self.mainLayout = QVBoxLayout();
		self.mainLayout.addWidget(self.label)
		self.mainLayout.addWidget(self.localRadioButton)
		self.mainLayout.addWidget(self.remoteRadioButton)
		self.setLayout(self.mainLayout)

		self.registerField("localClient",  self.localRadioButton)

class connectionPage(QWizardPage):
	def __init__(self, parent = None):
		QWizardPage.__init__(self,  parent)
		self.setTitle(self.tr("Pripojenie na BOINC"))
		self.setSubTitle(self.tr("Nastavenie pripojenia na klienta BOINC"))

		self.urlLabel = QLabel(self.tr("Cesta ku klientovi"))
		self.urlLayout = QHBoxLayout()
		
		self.urlLineEdit = QLineEdit()
		self.urlButton = QPushButton(self.tr("Vybrat adresar"))
		self.urlLayout.addWidget(self.urlLineEdit)
		self.urlLayout.addWidget(self.urlButton)
		self.urlText = QLabel()
		
		self.hostLabel = QLabel(self.tr("Adresa pocitacaa na ktorom bezi BOINC"))
		self.hostLineEdit = QLineEdit(self.tr("localhost"))
		
		self.portLabel = QLabel(self.tr("Port na ktorom bezi BOINC"))
		self.portSpinBox = QSpinBox()
		self.portSpinBox.setMinimum(1)
		self.portSpinBox.setMaximum(65535)
		self.portSpinBox.setValue(31416)
		
		self.passLabel = QLabel(self.tr("Heslo na pristup ku klientovi"))
		self.passLineEdit = QLineEdit()
		#self.passLineEdit.setEchoMode(QLineEdit.PasswordEchoOnEdit)

		self.mainLayout = QGridLayout()
		self.setLayout(self.mainLayout)
		self.mainLayout.addWidget(self.urlLabel, 0, 0)
		self.mainLayout.addLayout(self.urlLayout, 0, 1)
		self.mainLayout.addWidget(self.urlText, 1, 0, 1, 3)
		self.mainLayout.addWidget(self.hostLabel, 2, 0)
		self.mainLayout.addWidget(self.hostLineEdit, 2, 1, 1, 2)
		self.mainLayout.addWidget(self.portLabel, 3, 0)
		self.mainLayout.addWidget(self.portSpinBox, 3, 1, 1, 2)
		self.mainLayout.addWidget(self.passLabel, 4, 0)
		self.mainLayout.addWidget(self.passLineEdit, 4, 1, 1, 2)

		self.connect(self.urlButton, SIGNAL("clicked()"), self.getDirectory)
		self.connect(self.urlLineEdit, SIGNAL("textChanged(QString)"), self.emitChanged)

		self.registerField("clientURL", self.urlLineEdit)
		self.registerField("clientHost", self.hostLineEdit)
		self.registerField("clientPort", self.portSpinBox)
		self.registerField("clientPass", self.passLineEdit)
	
	def emitChanged(self):
		self.emit(SIGNAL("completeChanged()"))
	
	def initializePage(self):
		localClient = self.field("localClient").toBool()
		if not localClient:
			self.urlLabel.hide()
			self.urlLineEdit.hide()
			self.urlButton.hide()
			self.urlText.hide()
			self.passLineEdit.setReadOnly(False)
		else:
			self.urlLabel.show()
			self.urlLineEdit.show()
			self.urlButton.show()
			self.urlText.show()
			self.passLineEdit.setReadOnly(True)

	def getDirectory(self):
		dir = QFileDialog.getExistingDirectory(self, self.tr("Adresar s beziacim klientom BOINC"))
		if not dir.isNull():
			self.urlLineEdit.setText(dir)

	def getFullPath(self, path):
		file = QFSFileEngine(path)
		return file.fileName(QAbstractFileEngine.AbsoluteName)
	
	def setFileText(self,  text):
		self.urlText.setText(text)

	def isComplete(self):
		localClient = self.field("localClient").toBool()
		if not localClient:
			return True
		fullPath = self.getFullPath(self.urlLineEdit.text()+"/gui_rpc_auth.cfg")
		if not QFile.exists(fullPath):
			self.setFileText(QString("Subor %1 neexistuje").arg(fullPath))
			return False
		else:
			self.setFileText(QString("Autorizacny subor je %1").arg(fullPath))
			try:
				file = open(fullPath, "r")
				text = file.read()
				file.close()
				self.passLineEdit.setText(text)
			except Exception:
				pass
		return True

class addClientWizard(QWizard):
	def __init__(self, parent = None):
		QWizardPage.__init__(self, parent)
		self.setWindowTitle(self.tr("Pridat klienta"))
		self.addPage(introPage())
		self.addPage(connectionPage())
	
	def accept(self):
		QDialog.accept(self)
		localClient  = self.field("localClient").toBool()
		clientURL    = self.field("clientURL").toString()
		clientHost   = self.field("clientHost").toString()
		clientPort   = self.field("clientPort").toInt()
		clientPass   = self.field("clientPass").toString()

		self.emit(SIGNAL("wizardFinished(bool, QString, QString, int, QString)"), localClient, clientURL, clientHost, clientPort[0], clientPass)
