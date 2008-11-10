#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from Boinc.connectionmanager import ConnectionManager
from BoincGui.mainwindow import MainWindow
from PyQt4.QtGui import QApplication
from PyQt4.QtCore import QCoreApplication, QLocale, QTranslator
import sys
import gc


def main():
	gc.set_debug(gc.DEBUG_UNCOLLECTABLE | gc.DEBUG_SAVEALL| gc.DEBUG_INSTANCES | gc.DEBUG_OBJECTS)
	qtTranslator = QTranslator()
	qtTranslator.load("qt_" + QLocale.system().name())
	appTranslator = QTranslator()
	appTranslator.load("translations/boincgui_"  + QLocale.system().name())

	QCoreApplication.setOrganizationName("LinuxOS.sk")
	QCoreApplication.setOrganizationDomain("linuxos.sk")
	QCoreApplication.setApplicationName("pyboincgui")
	cm = ConnectionManager()
	app = QApplication(sys.argv)
	app.installTranslator(qtTranslator)
	app.installTranslator(appTranslator)
	win = MainWindow(cm)
	win.show()
	ret = app.exec_()

	del win
	del cm


if __name__ == "__main__":
	main ()
