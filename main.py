#!/usr/bin/env python
from Boinc.connectionmanager import ConnectionManager
from BoincGui.mainwindow import MainWindow
from PyQt4.QtGui import QApplication
from PyQt4.QtCore import QCoreApplication
import sys

def main():
	QCoreApplication.setOrganizationName ("LinuxOS.sk")
	QCoreApplication.setOrganizationDomain ("linuxos.sk")
	QCoreApplication.setApplicationName ("pyboincgui")
	cm = ConnectionManager()
	app = QApplication(sys.argv)
	win = MainWindow(cm)
	win.show()
	sys.exit(app.exec_())

if __name__ == "__main__":
	main ()
