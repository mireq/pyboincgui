from PyQt4.QtGui import QWidget, QPainter, QMatrix, QPalette, QFrame, QVBoxLayout, QRadialGradient, QColor
from PyQt4.QtCore import Qt, QSize, QRect, QPointF, QPoint
from math import sin, cos, pi

class PieChart(QWidget):
	__startAngle = 0
	__polozky = []

	def __init__(self, parent = None):
		QWidget.__init__(self, parent)

	def paintEvent(self, event):
		painter = QPainter(self)
		painter.setRenderHint(QPainter.Antialiasing)
		size = QSize(1, 1)
		size.scale(self.width() - 1, self.height() - 1, Qt.KeepAspectRatio)

		matrix = QMatrix()
		matrix.translate((self.width() - size.width()) / 2, (self.height() - size.height()) / 2)
		painter.setMatrix(matrix)
		self.__startAngle = 0
		for polozka in self.__polozky:
			self.kresliPolozku(painter, size, polozka[0], polozka[1], polozka[2])

	def kresliPolozku(self, painter, size, angle, nazov, color):
		col1 = QColor(color)
		col2 = QColor(color)
		col3 = QColor(color)
		col1 = col1.lighter(105)
		col2 = col1.darker(140)
		col3 = col3.darker()
		gradient = QRadialGradient(QPointF(size.width() / 2, size.height() / 2), size.width() / 2 - 20)
		gradient.setColorAt(0.0, col1)
		gradient.setColorAt(0.6, col2)
		gradient.setColorAt(1.0, col3)
		painter.setPen(Qt.NoPen)
		painter.setBrush(gradient)
		painter.drawPie(QRect(20, 20, size.width() - 40, size.height() - 40), self.__startAngle, angle)


		x = 0;
		y = 0;

		start = float(self.__startAngle) / 16.0;
		end   = float(self.__startAngle + angle) / 16.0;
		a = (start + end) / 2.0;
		x = cos((180.0 + a) / 180.0 * pi) * (size.width() / 2.5)
		y = sin(a / 180.0 * pi) * (size.height() / 2.5)

		font = self.font()
		font.setBold(True)
		painter.setFont(font)

		painter.setOpacity(0.5);
		painter.setPen(Qt.black)
		painter.drawText(QRect(size.width() / 2 - x - 99, size.height() / 2 - y -19, 200, 40), Qt.AlignCenter, nazov)
		painter.setOpacity(0.8);
		painter.setPen(Qt.white)
		painter.drawText(QRect(size.width() / 2 - x - 100, size.height() / 2 - y -20, 200, 40), Qt.AlignCenter, nazov)
		painter.setOpacity(1.0);
		self.__startAngle = self.__startAngle + angle


	def minimumSizeHint(self):
		return QSize(80, 80)

	def itemsCount(self):
		return len(self.__polozky)

	def removeItem(self, index):
		self.__polozky.pop(index)
		self.update()

	def addItem(self, size, name, color):
		self.__polozky.append([size, name, color])
		self.update()

	def removeItems(self):
		self.__polozky = []
		self.update()

class PieChartFrame(QFrame):
	__chart = None;

	def __init__(self, parent = None):
		QFrame.__init__(self, parent)
		self.setAutoFillBackground(True)
		self.setFrameStyle(QFrame.Box)
		self.setFrameShadow(QFrame.Sunken)
		self.setBackgroundRole(QPalette.Base)

		self.__chart = PieChart()
		mainLayout = QVBoxLayout();
		mainLayout.addWidget(self.__chart)
		self.setLayout(mainLayout)

	def addItem(self, size, name, color):
		self.__chart.addItem(size, name, color)

	def removeItem(self, index):
		self.__chart.removeItem(index)

	def removeItems(self):
		self.__chart.removeItems()

	def itemsCount(self):
		return self.__chart.itemsCount()