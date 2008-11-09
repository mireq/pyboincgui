from PyQt4.QtCore import SIGNAL, SLOT
from PyQt4.QtGui import QMainWindow, QMenuBar, QMenu, QAction, QKeySequence, qApp, QWidget
from addclientwizard import addClientWizard
from mainwidget import mainWidget
from Boinc.connection import BoincConnectionException
from Boinc.interface import BoincCommException
from threading import Thread
import sys

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
		self.queueThread = Thread(target = self.processQueue, args = (self.connManager.queue(), ))
		self.queueThread.start()
		self.connManager.loadConnections()
		self.connManager.addConnection(True, "/home/mirec/Documents/Moje/Programy/python/test", "localhost", 31416, "a721410eeb1aefb913a3766a9297ce56", True)
		self.resize(800, 500)

	def processQueue(self, queue):
		while True:
			item = queue.get()
			if isinstance(item, Exception):
				if isinstance(item, BoincConnectionException):
					sys.stdout.write(self.tr(u"Connection error: %1").arg(item[0]))
				elif isinstance(item, BoincCommException):
					sys.stdout.write(self.tr(u"Communication error: %1").arg(item[0]))
				elif isinstance(item, Exception):
					sys.stdout.write(self.tr(u"Unknown error: %1").arg(item[0]))
					raise item
				sys.stdout.flush()
			queue.task_done()

	def createMainWin(self):
		self.centralWidget = mainWidget(self.connManager)
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
