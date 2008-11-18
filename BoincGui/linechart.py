from PyQt4.QtGui import QFrame, QWidget, QPalette, QVBoxLayout, QPainter, QPen, QBrush, QColor, QPalette, QPainterPath, QSizePolicy
from PyQt4.QtCore import QSize, QRect, QPoint, Qt

class LineChart(QWidget):
	__graphs = []
	__padding = 5
	__index = 0

	def __init__(self, parent = None):
		QWidget.__init__(self, parent)
		self.removeGraphs()
		self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

	def minimumSizeHint(self):
		return QSize(50, 50)

	def addGraph(self, data, name, color):
		if len(data) == 0:
			return

		if self.__minDay == 0:
			self.__minDay = data[0].day
		if data[0].day < self.__minDay:
			self.__minDay = data[0].day
		if data[len(data) - 1].day > self.__maxDay:
			self.__maxDay = data[len(data) - 1].day

		if self.__minPoints == 0:
			self.__minPoints = data[0].data(self.__index)
		if data[0].data(self.__index) < self.__minPoints:
			self.__minPoints = data[0].data(self.__index)
		if data[len(data) - 1].data(self.__index) > self.__maxPoints:
			self.__maxPoints = data[len(data) - 1].data(self.__index)

		self.__graphs.append((data, name, color))		
		self.update()

	def removeGraphs(self):
		self.__graphs = []
		self.__minDay = 0
		self.__maxDay = 0
		self.__minPoints = 0
		self.__maxPoints = 0

	def paintEvent(self, event):
		palette = QPalette()
		painter = QPainter(self)
		#painter.setRenderHint(QPainter.Antialiasing)

		if (not self.__minDay == self.__maxDay) and (not self.__minPoints == self.__maxPoints):
			ciara = QPen(palette.color(QPalette.WindowText))
			pozadieBaseColor = QColor(palette.color(QPalette.Base))
			pozadieMixColor = QColor(90, 150, 250);
			red   = (pozadieBaseColor.red() + pozadieMixColor.red()) / 2
			green = (pozadieBaseColor.green() + pozadieMixColor.green()) / 2
			blue  = (pozadieBaseColor.blue() + pozadieMixColor.blue()) / 2
			pozadieColor = QColor(red, green, blue);
			pozadie = QBrush(pozadieColor)

			painter.setPen(ciara)
			painter.setBrush(pozadie)

			painter.translate(5, 5)
			rect = QRect(0, 0, self.width() - (2 * self.__padding), self.height() - (2 * self.__padding))
			painter.drawRect(rect)
			self.__drawLines(painter, self.width() - (2 * self.__padding), self.height() - (2 * self.__padding))

	def __drawLines(self, painter, width, height):
		painter.setRenderHint(QPainter.Antialiasing)
		for graph in self.__graphs:
			self.__drawLine(painter, graph, width, height)

	def __getCoordinates(self, width, height, xdata, ydata):
		x = int(float(xdata - self.__minDay) / float(self.__maxDay - self.__minDay) * float(width))
		y = height - int(float(ydata - self.__minPoints) / float(self.__maxPoints - self.__minPoints) * float(height))
		return (x, y)

	def __drawLine(self, painter, graph, width, height):
		path = QPainterPath()
		try:
			day   = graph[0][0].day
			value = graph[0][0].data(self.__index)
			(x, y) = self.__getCoordinates(width, height, day, value)
			path.moveTo(x, y)
		except IndexError:
			pass

		for pos in range(1, len(graph[0])):
			point = graph[0][pos]
			day   = point.day
			value = point.data(self.__index)
			(x, y) = self.__getCoordinates(width, height, day, value)
			path.lineTo(x, y)

		pen = QPen()
		pen.setColor(QColor(graph[2]))
		pen.setWidth(3)
		pen.setCapStyle(Qt.RoundCap);
 		pen.setJoinStyle(Qt.RoundJoin);
		painter.setPen(pen)
		painter.drawPath(path)

class LineChartFrame(QFrame):
	__chart = None;

	def __init__(self, parent = None):
		QFrame.__init__(self, parent)
		self.setAutoFillBackground(True)
		self.setFrameStyle(QFrame.Box)
		self.setFrameShadow(QFrame.Sunken)
		self.setBackgroundRole(QPalette.Base)

		self.__chart = LineChart()
		mainLayout = QVBoxLayout();
		mainLayout.addWidget(self.__chart)
		self.setLayout(mainLayout)

	def addGraph(self, data, name, color):
		self.__chart.addGraph(data, name, color)

	def removeGraphs(self):
		self.__chart.removeGraphs()
