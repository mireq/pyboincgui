from PyQt4.QtGui import QVBoxLayout, QLabel, QWidget, QSizePolicy, QFont, QHBoxLayout, QFrame, QPalette, QPixmap, QIcon
from PyQt4.QtCore import Qt


class titleFrame(QWidget):
	__text = ""
	__icon = None

	__mainLayout = None

	__label = None
	__iconLabel = None

	__kde = False

	def __init__(self, text, icon = None, parent = None):
		QWidget.__init__(self, parent)
		self.__text = text
		self.__icon = icon

		self.__topLayout = QVBoxLayout()
		self.setLayout(self.__topLayout)

		try:
			from PyKDE4.kdeui import KTitleWidget
			self.__titleWidget = KTitleWidget()
			self.__topLayout.addWidget(self.__titleWidget)
			self.__kde = True
		except:
			self.__mainFrame = QFrame()
			self.__topLayout.addWidget(self.__mainFrame)
			self.__label = QLabel()
			self.__iconLabel = QLabel()

			self.__mainLayout = QHBoxLayout()
			self.init()

		self.setText(text)
		if not icon is None:
			self.setIcon(icon)

	def init(self):
		self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
		font = QFont()
		font.setBold(True)
		font.setItalic(True)
		self.__label.setFont(font)

		self.__mainLayout.setAlignment(Qt.AlignVCenter)
		self.__mainLayout.addWidget(self.__iconLabel)
		self.__mainLayout.addWidget(self.__label)
		self.__mainLayout.addStretch(1)

		self.__mainFrame.setAutoFillBackground(True)
		self.__mainFrame.setFrameStyle(QFrame.Box)
		self.__mainFrame.setFrameShadow(QFrame.Sunken)
		self.__mainFrame.setBackgroundRole(QPalette.Base)

		self.__mainFrame.setLayout(self.__mainLayout)

	def setText(self, text):
		if self.__kde:
			self.__titleWidget.setText(text)
		else:
			self.__label.setText(text)

	def setIcon(self, icon):
		if self.__kde:
			self.__titleWidget.setPixmap(QPixmap(icon))
		else:
			self.__iconLabel.setPixmap(QPixmap(icon))
