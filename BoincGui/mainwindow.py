from PyQt4.QtCore import SIGNAL, SLOT
from PyQt4.QtGui import QMainWindow, QMenuBar, QMenu, QAction, QKeySequence, qApp
from addclientwizard import addClientWizard

class MainWindow(QMainWindow):
    def __init__(self,  parent = None):
        QMainWindow.__init__(self,  parent)
        self.setWindowTitle(self.tr("Boinc gui"))
        self.createActions()
        self.createMenu()
        
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
        self.wizardWin.setModal(True)
        self.wizardWin.show()
