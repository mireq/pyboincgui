from PyQt4.QtGui import QLabel, QWidget, QSizePolicy, QFont, QHBoxLayout, QFrame, QPalette, QPixmap
from PyQt4.QtCore import Qt

class headerFrame(QFrame):
	__text = ""
	__icon = None

	__mainLayout = None

	__label = None
	__iconLabel = None

	def __init__(self, text, icon = None, parent = None):
		QFrame.__init__(self, parent)
		self.__text = text
		self.__icon = icon

		self.__label = QLabel()
		self.__iconLabel = QLabel()

		self.__mainLayout = QHBoxLayout()

		self.setText(text)
		if not icon is None:
			self.setIcon(icon)
		self.init()

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

		self.setFrameStyle(QFrame.StyledPanel)
		self.setAutoFillBackground(True)
		self.setBackgroundRole(QPalette.Base)

		self.setLayout(self.__mainLayout)

	def setText(self, text):
		self.__label.setText(text)

	def setIcon(self, icon):
		self.__iconLabel.setPixmap(QPixmap(icon))
