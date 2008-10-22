from PyQt4.QtCore import SIGNAL, SLOT
from PyQt4.QtGui import QMainWindow, QMenuBar, QMenu, QAction, QKeySequence, qApp, QWidget
from addclientwizard import addClientWizard
from mainwidget import mainWidget

class MainWindow(QMainWindow):
	connManager = None
	def __init__(self, manager, parent = None):
		QMainWindow.__init__(self,  parent)
		self.connManager = manager
		self.setWindowTitle(self.tr("Boinc gui"))
		self.createActions()
		self.createMenu()
		self.createMainWin()
		self.statusBar().showMessage(self.tr("Ready"), 3000)

	def createMainWin(self):
		self.centralWidget = mainWidget()
		self.setCentralWidget(self.centralWidget)

	def createActions(self):
		self.addClientAction = QAction(self.tr("&Add Client"),  self)
		self.quitAction = QAction(self.tr("&Quit"), self)

		#pridavame klavesove skratky
		self.quitAction.setShortcut(QKeySequence(self.tr("Ctrl+Q")))

		#prepojime akcie so slotmi
		self.connect(self.addClientAction, SIGNAL("triggered()"), self.showWizard)
		self.connect(self.quitAction, SIGNAL("triggered()"), qApp, SLOT("quit()"))

	def createMenu(self):
		fileMenu = self.menuBar().addMenu(self.tr("&File"))
		fileMenu.addAction(self.addClientAction)
		fileMenu.addAction(self.quitAction)

	def showWizard(self):
		self.wizardWin = addClientWizard(self)
		self.connect(self.wizardWin, SIGNAL("wizardFinished(bool, QString, QString, int, QString)"), self.processWizard)
		self.wizardWin.setModal(True)
		self.wizardWin.show()

	def processWizard(self, local, path, host, port, password):
		self.connManager.addConnection(local, path, host, port, password)
