from PyQt4.QtCore import SIGNAL, SLOT, QThread
from PyQt4.QtGui import QMainWindow, QMenuBar, QMenu, QAction, QKeySequence, qApp, QWidget, QMessageBox
from addclientwizard import addClientWizard
from mainwidget import mainWidget
from Boinc.connection import BoincConnectionException
from Boinc.interface import BoincCommException
import sys

class ProcessQueeueThread(QThread):
	__stop = False
	def __init__(self, queue, parent = None):
		QThread.__init__(self, parent)
		self.queue = queue
	def run(self):
		while True:
			item = self.queue.get()
			if self.__stop:
				return
			if isinstance(item, Exception):
				if isinstance(item, BoincConnectionException):
					sys.stdout.write(self.tr(u"Connection error: %1").arg(item[0]))
				elif isinstance(item, BoincCommException):
					sys.stdout.write(self.tr(u"Communication error: %1").arg(item[0]))
				elif isinstance(item, Exception):
					sys.stdout.write(self.tr(u"Unknown error: %1").arg(item[0]))
					raise item
				sys.stdout.flush()
			self.queue.task_done()

	def stop(self):
		self.__stop = True

class MainWindow(QMainWindow):
	__connManager = None
	__activeClient = -1
	def __init__(self, manager, parent = None):
		QMainWindow.__init__(self,  parent)
		self.__activeClient = -1
		self.__connManager = manager
		self.setWindowTitle(self.tr("Boinc gui"))
		self.createActions()
		self.createMenu()
		self.createMainWin()
		self.statusBar().showMessage(self.tr("Ready"), 3000)
		self.queueThread = ProcessQueeueThread(self.__connManager.queue(), self)
		self.queueThread.start()
		self.__connManager.loadConnections()
		self.resize(800, 500)

	def connManager(self):
		return self.__connManager

	def __del__(self):
		self.queueThread.stop()
		self.__connManager.queue().put("")
		self.queueThread.wait()

	def createMainWin(self):
		self.centralWidget = mainWidget(self.__connManager)
		self.connect(self.centralWidget, SIGNAL('clientChanged(int)'), self.changeClient)
		self.setCentralWidget(self.centralWidget)

	def changeClient(self, client):
		self.__activeClient = client
		if client == -1:
			self.remClientAction.setEnabled(False);
		else:
			self.remClientAction.setEnabled(True);

	def createActions(self):
		self.addClientAction = QAction(self.tr("&Add Client"),  self)
		self.remClientAction = QAction(self.tr("&Remove Client"),  self)
		self.quitAction = QAction(self.tr("&Quit"), self)

		#pridavame klavesove skratky
		self.quitAction.setShortcut(QKeySequence(self.tr("Ctrl+Q")))
		self.remClientAction.setEnabled(False);

		#prepojime akcie so slotmi
		self.connect(self.addClientAction, SIGNAL("triggered()"), self.showWizard)
		self.connect(self.remClientAction, SIGNAL("triggered()"), self.removeClient)
		self.connect(self.quitAction, SIGNAL("triggered()"), qApp, SLOT("quit()"))

	def removeClient(self):
		if self.__activeClient != -1:
			btn = QMessageBox.question(self, self.tr("Remove Client"), self.tr("Are you sure that you want to remove client?"), QMessageBox.Yes|QMessageBox.No)
			if btn == QMessageBox.Yes:
				self.__connManager.removeConnection(self.__activeClient)

	def createMenu(self):
		fileMenu = self.menuBar().addMenu(self.tr("&File"))
		fileMenu.addAction(self.addClientAction)
		fileMenu.addAction(self.remClientAction)
		fileMenu.addAction(self.quitAction)

	def showWizard(self):
		self.wizardWin = addClientWizard(self)
		self.connect(self.wizardWin, SIGNAL("wizardFinished(bool, QString, QString, int, QString)"), self.processWizard)
		self.wizardWin.setModal(True)
		self.wizardWin.show()

	def processWizard(self, local, path, host, port, password):
		self.__connManager.addConnection(local, path, host, port, password)
