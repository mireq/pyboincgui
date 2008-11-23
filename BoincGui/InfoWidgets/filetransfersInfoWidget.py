from infoWidget import infoWidget
from PyQt4.QtCore import Qt, SIGNAL, QTimer, QVariant, QString, QLocale
from PyQt4.QtGui import QVBoxLayout, QTreeWidget, QTreeWidgetItem, QProgressBar


class filetransfersInfoWidget(infoWidget):

	def __init__(self, client, parent = None):
		infoWidget.__init__(self, client, parent)

		self.__informations = []
		self.__loc = QLocale()
		self.__mainLayout = QVBoxLayout()
		self.__treeWidget = QTreeWidget()

		self.__treeWidget.setColumnCount(5)
		#stlpce projekt, nazov, progress, prenesene (kolko z kolko), rychlost
		labels = [self.tr("Project name"), self.tr("File name"), self.tr("Progress"), self.tr("Size"), self.tr("Speed")]
		self.__treeWidget.setHeaderLabels(labels)
		self.__treeWidget.setUniformRowHeights(True)

		self.__mainLayout.addWidget(self.__treeWidget)
		self.setMainLayout(self.__mainLayout)
		
		self.connect(client, SIGNAL("getFileTransfersRecv(PyQt_PyObject)"), self.__updateFileTransfers)
		client.getFileTransfers()

	def __jednotka(self, data):
		if data < 1024:
			return self.__loc.toString(int(data))+" B"
		elif data < 1024*1024:
			return self.__loc.toString(float(data) / float(1024), 'f', 2)+" kB"
		elif data < 1024*1024*1024:
			return self.__loc.toString(float(data) / float(1024*1024), 'f', 2)+" MB"
		elif data < 1024*1024*1024*1024:
			return self.__loc.toString(float(data) / float(1024*1024*1024), 'f', 2)+" GB"
		return self.__loc.toString(int(data))+" B"

	def __updateData(self, data, item, progressBar):
		if data['bytes_xferred'] is None:
			data['bytes_xferred'] = 0
			progressBar.setValue(0)
		else:
			progressBar.setValue(int(100.0 * data['bytes_xferred'] / data['nbytes']))
		item.setData(0, Qt.DisplayRole, QVariant(data['project_name']))
		item.setData(1, Qt.DisplayRole, QVariant(data['name']))
		if data['xfer_speed'] is None:
			data['xfer_speed'] = 0
		item.setData(3, Qt.DisplayRole, QVariant(self.__jednotka(data['bytes_xferred']) + '/' + self.__jednotka(data['nbytes'])))
		item.setData(4, Qt.DisplayRole, QVariant(self.__jednotka(data['xfer_speed'])+self.tr('/s')))


	def __updateFileTransfers(self, transfers):
		pridat = []

		for inf in self.__informations:
			inf[4] = True

		for transfer in transfers:
			pridame = True
			for inf in self.__informations:
				if inf[0] == (transfer['name'], transfer['project_url']):
					pridame = False
					inf[3] = transfer
					inf[4] = False
					break
			if pridame:
				pridat.append(transfer)

		for polozka in pridat:
			treeItem = QTreeWidgetItem(self.__treeWidget)
			progressBar = QProgressBar()
			progressBar.setAutoFillBackground(True)
			progressBar.setFixedHeight(self.__treeWidget.rowHeight(self.__treeWidget.indexFromItem(treeItem)))
			self.__treeWidget.setItemWidget(treeItem, 2, progressBar)
			self.__informations.append([(polozka['name'], polozka['project_url']), treeItem, progressBar, polozka, False])

			self.__updateData(polozka, treeItem, progressBar)

		for i in range(len(self.__informations) - 1, -1, -1):
			# odstranenie
			if self.__informations[i][4]:
				self.__treeWidget.takeTopLevelItem(i)
				self.__informations.pop(i)
			# aktualizacia
			else:
				inf = self.__informations[i]
				self.__updateData(inf[3], inf[1], inf[2])


		QTimer.singleShot(1000, self.sender().getFileTransfers)