from PyQt4.QtGui import QWidget, QLabel, QVBoxLayout

class clientInfoWidget(QWidget):
	def __init__(self, client, parent = None):
		QWidget.__init__(self, parent)
		self.mainLayout = QVBoxLayout()
		self.setLayout(self.mainLayout)

		self.mainLayout.addWidget(QLabel("Hello world"))