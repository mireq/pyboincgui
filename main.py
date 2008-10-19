#!/usr/bin/env python
from Boinc.Interface import Interface
from BoincGui.mainwindow import MainWindow
from PyQt4.QtGui import QApplication
import sys

def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show() 
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
