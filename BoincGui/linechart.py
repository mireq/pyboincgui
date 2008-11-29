from PyQt4.QtGui import QFrame, QWidget, QPalette, QVBoxLayout, QPainter, QPen, QBrush, QColor, QPalette, QPainterPath, QSizePolicy, QMatrix, QFontMetrics
from PyQt4.QtCore import QSize, QRect, QPoint, Qt, QString, QLocale, QDateTime

class LineChart(QWidget):
	__graphs = []
	__padding = 5
	__index = 0

	__xMedzery = 100
	__yMedzery = 30

	def __init__(self, parent = None):
		QWidget.__init__(self, parent)
		self.removeGraphs()
		self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

	def minimumSizeHint(self):
		return QSize(50, 50)

	def __initRange(self):
		self.__minDay = 0
		self.__maxDay = 0
		self.__minPoints = 0
		self.__maxPoints = 0

	def __recompRange(self):
		self.__initRange()
		for graph in self.__graphs:
			data = graph[0]

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
		self.__initRange()
		self.update()

	def __calcCoordRanges(self):
		self.__xRange = self.__maxDay - self.__minDay
		self.__yRange = self.__maxPoints - self.__minPoints
		self.__xMin = self.__minDay - int(float(self.__xRange) * 0.01)
		self.__xMax = self.__maxDay + int(float(self.__xRange) * 0.01)
		self.__yMin = self.__minPoints - int(float(self.__yRange) * 0.01)
		self.__yMax = self.__maxPoints + int(float(self.__yRange) * 0.01)

	def paintEvent(self, event):
		painter = QPainter(self)

		if (not self.__minDay == self.__maxDay) and (not self.__minPoints == self.__maxPoints):
			self.__calcCoordRanges()
			(xVelkost, yVelkost) = self.__drawAxes(painter)
			self.__drawLines(painter, xVelkost, yVelkost)

	def __calcAxesData(self, size, space, dataMin, dataMax):
		kroky = float(size) / float(space)
		rozsah = float(dataMax - dataMin)
		krok = rozsah / kroky;

		mocnina = -1
		cislo = 10
		zaokruhlenyKrok = cislo**mocnina
		while zaokruhlenyKrok < krok:
			if zaokruhlenyKrok * 2 >= krok:
				zaokruhlenyKrok = zaokruhlenyKrok * 2
				break
			if zaokruhlenyKrok * 5 >= krok:
				zaokruhlenyKrok = zaokruhlenyKrok * 5
				break
			mocnina = mocnina + 1
			zaokruhlenyKrok = cislo**mocnina

		hodnoty = []
		for i in range(int(dataMin / zaokruhlenyKrok), int(dataMax / zaokruhlenyKrok + 1)):
			hodnota = i * zaokruhlenyKrok
			if hodnota >= dataMin and hodnota <= dataMax:
				hodnoty.append(hodnota)
		return hodnoty

	def __calcMaxTextSize(self, font, hodnoty):
		fm = QFontMetrics(font);
		x = 0
		y = fm.height()
		for hodnota in hodnoty:
			w = fm.width(hodnota)
			if w > x:
				x = w
		return (x, y)

	def __convertXData(self, data):
		loc = QLocale()
		out = []
		for polozka in data:
			time = QDateTime()
			time.setTime_t(polozka)
			out.append(time.toString(loc.dateFormat(QLocale.ShortFormat)))
		return out

	def __convertYData(self, data):
		loc = QLocale()
		out = []
		for polozka in data:
			out.append(loc.toString(polozka))
		return out

	def __drawAxes(self, painter):
		"""
		Pozor, tato metoda vracia nove velkosti X a Y pretoze pri kresleni osi
		sa rata aj s velkostou textu ktora je variabilna
		"""

		palette = QPalette()
		penColor = QColor(palette.color(QPalette.WindowText))
		ciara = QPen(penColor)
		pozadieBaseColor = QColor(palette.color(QPalette.Base))
		pozadieMixColor = QColor(90, 150, 250);
		red   = (pozadieBaseColor.red() * 4 + pozadieMixColor.red()) / 5
		green = (pozadieBaseColor.green() * 4 + pozadieMixColor.green()) / 5
		blue  = (pozadieBaseColor.blue() * 4 + pozadieMixColor.blue()) / 5
		pozadieColor = QColor(red, green, blue);
		pozadie = QBrush(pozadieColor)

		painter.setPen(ciara)
		painter.setBrush(pozadie)

		xVelkost = self.width() - (2 * self.__padding)
		yVelkost = self.height() - (2 * self.__padding)
		xOs = self.__calcAxesData(xVelkost, self.__xMedzery, self.__minDay, self.__maxDay)
		yOs = self.__calcAxesData(yVelkost, self.__yMedzery, self.__minPoints, self.__maxPoints)

		xText = self.__convertXData(xOs)
		yText = self.__convertYData(yOs)

		(xxText, xyText) = self.__calcMaxTextSize(self.font(), xText)
		(yxText, yyText) = self.__calcMaxTextSize(self.font(), yText)

		xVelkost = xVelkost - yxText
		yVelkost = yVelkost - xyText

		painter.translate(yxText + 5, 5)
		rect = QRect(0, 0, xVelkost, yVelkost)
		painter.drawRect(rect)

		penColor.setAlpha(60)
		painter.setPen(QPen(penColor))

		for hodnota in yOs:
			y = self.__getYCoord(yVelkost, hodnota)
			painter.drawLine(0, y, xVelkost, y)
		for hodnota in xOs:
			x = self.__getXCoord(xVelkost, hodnota)
			painter.drawLine(x, 0, x, yVelkost)

		painter.setPen(palette.color(QPalette.WindowText))

		for i in range(len(yText)):
			hodnota = yOs[i]
			text = yText[i]
			y = self.__getYCoord(yVelkost, hodnota)
			textRect = QRect(-yxText-3, y - yyText / 2, yxText, yyText)
			painter.drawText(textRect, Qt.AlignRight, text)
		for i in range(len(xText)):
			hodnota = xOs[i]
			text = xText[i]
			x = self.__getXCoord(xVelkost, hodnota)
			textRect = QRect(x - xxText / 2, yVelkost + xyText / 2, xxText, xyText)
			painter.drawText(textRect, Qt.AlignHCenter, text)
		return (xVelkost, yVelkost)

	def __drawLines(self, painter, width, height):
		painter.setRenderHint(QPainter.Antialiasing)
		for graph in self.__graphs:
			self.__drawLine(painter, graph, width, height)

	def __getXCoord(self, width, xdata):
		return int(float(xdata - self.__xMin) / float(self.__xMax - self.__xMin) * float(width))

	def __getYCoord(self, height, ydata):
		return height - int(float(ydata - self.__yMin) / float(self.__yMax - self.__yMin) * float(height))

	def __getCoordinates(self, width, height, xdata, ydata):
		x = self.__getXCoord(width, xdata)
		y = self.__getYCoord(height, ydata)
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
		painter.setBrush(Qt.NoBrush)
		painter.drawPath(path)

	def setIndex(self, index):
		self.__index = index
		self.__recompRange()
		self.update()

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

	def setIndex(self, index):
		self.__chart.setIndex(index)
