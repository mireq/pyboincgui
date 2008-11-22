from PyQt4.QtGui import QWidget, QLabel, QGridLayout, QVBoxLayout, QHBoxLayout, QScrollArea, QFrame
from PyQt4.QtCore import Qt, SIGNAL

class infoWidget(QWidget):

	__mainLayout = None
	__connLayout = None
	__title  = None
	__layout = None

	__scrollArea   = None
	__scrollWidget = None

	__connGroupBox = None

	__advClientInfoLayout   = None
	__advClientInfoGroupBox = None

	__client = None

	def __init__(self, client, parent = None):
		QWidget.__init__(self, parent)
		self.__client = client
		self.__mainLayout = QVBoxLayout(self)

	def setMainLayout(self, layout, scroll = True):
		if not self.__layout is None:
			self.__mainLayout.removeItem(self.__layout)
		if not self.__scrollArea is None:
			self.__mainLayout.removeWidget(self.__scrollArea)

		self.__layout = None
		self.__scrollArea   = None
		self.__scrollWidget = None

		if not layout is None:
			if scroll:
				self.__scrollWidget = QWidget()
				self.__scrollWidget.setLayout(layout)

				self.__scrollArea = QScrollArea()
				self.__scrollArea.setWidgetResizable(True)
				self.__scrollArea.setWidget(self.__scrollWidget)
				self.__scrollArea.setFrameStyle(QFrame.NoFrame)
				self.__scrollArea.setFrameShadow(QFrame.Plain)

				self.__mainLayout.addWidget(self.__scrollArea)

			else:
				self.__mainLayout.addLayout(layout)
			self.__layout = layout
		else:
			self.__layout = layout

	def setTitle(self, title):
		if not self.__title is None:
			self.__mainLayout.removeWidget(self.__title)
			self.__title.deleteLater()

		if not title is None:
			self.__mainLayout.insertWidget(0, title)
		self.__title = title;

	def __del__(self):
		self.__client = None

	def client(self):
		return self.__client