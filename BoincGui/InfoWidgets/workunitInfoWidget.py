from infoWidget import infoWidget
from PyQt4.QtGui import QGridLayout, QVBoxLayout, QLabel, QProgressBar, QGroupBox
from PyQt4.QtCore import Qt, SIGNAL, QString, QLocale, QTime, QDateTime, QChar

class workunitInfoWidget(infoWidget):

	__masterURL = ""
	__name = ""

	__mainLayout = None
	

	__wuNameLabel = None
	__reportDeadlineLabel = None
	__estimatedCpuTimeRemainingLabel = None
	__fractionDoneLabel = None
	__currentCpuTimeLabel = None

	__progressBar = None
	__taskInfoGBox = None
	__activeTaskInfoGBox = None

	# pre vsetky
	__wuName = ""
	__estimatedCpuTimeRemaining = 0
	__reportDeadline = 0

	#len aktivne
	__fractionDone = 0.0
	__currentCpuTime = 0

	def __init__(self, client, project, workunit, parent = None):
		infoWidget.__init__(self, client, parent)

		self.__mainLayout = QVBoxLayout()
		self.setMainLayout(self.__mainLayout)

		self.__wuNameLabel                    = QLabel()
		self.__reportDeadlineLabel            = QLabel(self.tr("Report deadline:"))
		self.__estimatedCpuTimeRemainingLabel = QLabel(self.tr("Estimated CPU time remaining:"))
		self.__fractionDoneLabel              = QLabel(self.tr("Fraction done:"))
		self.__currentCpuTimeLabel            = QLabel(self.tr("Current CPU time:"))

		self.__reportDeadlineText            = QLabel()
		self.__estimatedCpuTimeRemainingText = QLabel()
		self.__fractionDoneText              = QLabel()
		self.__currentCpuTimeText            = QLabel()

		self.__progressBar = QProgressBar()
		self.__progressBar.setMaximum(10000);

		self.__wuNameLabel.setTextFormat(Qt.PlainText)
		self.__estimatedCpuTimeRemainingLabel.setTextFormat(Qt.PlainText)
		self.__reportDeadlineLabel.setTextFormat(Qt.PlainText)
		self.__fractionDoneLabel.setTextFormat(Qt.PlainText)
		self.__currentCpuTimeLabel.setTextFormat(Qt.PlainText)

		self.__estimatedCpuTimeRemainingText.setTextFormat(Qt.PlainText)
		self.__reportDeadlineText.setTextFormat(Qt.PlainText)
		self.__fractionDoneText.setTextFormat(Qt.PlainText)
		self.__currentCpuTimeText.setTextFormat(Qt.PlainText)

		self.__wuNameLabel.setWordWrap(True)
		self.__estimatedCpuTimeRemainingLabel.setWordWrap(True)
		self.__reportDeadlineLabel.setWordWrap(True)
		self.__fractionDoneLabel.setWordWrap(True)
		self.__currentCpuTimeLabel.setWordWrap(True)

		self.__estimatedCpuTimeRemainingText.setWordWrap(True)
		self.__reportDeadlineText.setWordWrap(True)
		self.__fractionDoneText.setWordWrap(True)
		self.__currentCpuTimeText.setWordWrap(True)

		self.__taskInfoGBox = QGroupBox(self.tr("Task info"))
		self.__activeTaskInfoGBox = QGroupBox(self.tr("Active task info"))

		self.__taskInfoLayout = QGridLayout()
		self.__activeTaskInfoLayout = QGridLayout()

		self.__taskInfoGBox.setLayout(self.__taskInfoLayout)
		self.__activeTaskInfoGBox.setLayout(self.__activeTaskInfoLayout)

		self.__mainLayout.addWidget(self.__taskInfoGBox)
		self.__mainLayout.addWidget(self.__activeTaskInfoGBox)
		self.__mainLayout.addStretch(1)
		self.__mainLayout.addWidget(self.__progressBar)

		self.__taskInfoLayout.addWidget(self.__wuNameLabel, 0, 0, 1, 2)
		self.__taskInfoLayout.addWidget(self.__reportDeadlineLabel, 1, 0)
		self.__taskInfoLayout.addWidget(self.__estimatedCpuTimeRemainingLabel, 2, 0)
		self.__taskInfoLayout.addWidget(self.__reportDeadlineText, 1, 1)
		self.__taskInfoLayout.addWidget(self.__estimatedCpuTimeRemainingText, 2, 1)

		self.__activeTaskInfoLayout.addWidget(self.__fractionDoneLabel, 0, 0)
		self.__activeTaskInfoLayout.addWidget(self.__currentCpuTimeLabel, 1, 0)
		self.__activeTaskInfoLayout.addWidget(self.__fractionDoneText, 0, 1)
		self.__activeTaskInfoLayout.addWidget(self.__currentCpuTimeText, 1, 1)

		#self.__mainLayout.addWidget(self.__wuNameLabel, 0, 0, 1, 2)
		#self.__mainLayout.addWidget(self.__estimatedCpuTimeRemainingLabel, 1, 0)
		#self.__mainLayout.addWidget(self.__reportDeadlineLabel, 1, 1)
		#self.__mainLayout.addWidget(self.__fractionDoneLabel, 2, 0)
		#self.__mainLayout.addWidget(self.__currentCpuTimeLabel, 2, 1)
		#self.__mainLayout.setRowStretch(3, 1)
		#self.__mainLayout.addWidget(self.__progressBar, 4, 0, 1, 2)

		self.__masterURL = project.data(0, Qt.UserRole + 1).toString()
		self.__name = workunit.data(0, Qt.UserRole + 1).toString()

		projects = client.projectState()
		if not projects is None:
			self.updateProjects(projects)
		self.connect(client, SIGNAL("projectState(PyQt_PyObject)"), self.updateProjects)

	def __getTimeString(self, time):
		days = time / 86400
		estCpuTimeRem = QTime(0, 0, 0, 0)
		estCpuTimeRem = estCpuTimeRem.addSecs(time)

		deadline = QDateTime()
		deadline.setTime_t(self.__reportDeadline)

		if days > 0:
			return QString(self.tr("%n day(s), %1:%2:%3", "", days).arg(estCpuTimeRem.hour(), 2, 10, QChar('0')).arg(estCpuTimeRem.minute(), 2, 10, QChar('0')).arg(estCpuTimeRem.second(), 2, 10, QChar('0')))
		else:
			return QString(self.tr("%1:%2:%3").arg(estCpuTimeRem.hour(), 2, 10, QChar('0')).arg(estCpuTimeRem.minute(), 2, 10, QChar('0')).arg(estCpuTimeRem.second(), 2, 10, QChar('0')))

	def updateProjects(self, projects):
		result = None
		results = projects['result']

		for res in results:
			if res['project_url'] == self.__masterURL and res['name'] == self.__name:
				result = res;
				break

		if result is None:
			return

		loc = QLocale()
		currTime = QDateTime.currentDateTime()

		self.__wuName = result['wu_name'];
		self.__estimatedCpuTimeRemaining = int(float(result['estimated_cpu_time_remaining']))
		self.__reportDeadline = int(float(result['report_deadline']))

		days = self.__estimatedCpuTimeRemaining / 86400
		estCpuTimeRem = QTime(0, 0, 0, 0)
		estCpuTimeRem = estCpuTimeRem.addSecs(self.__estimatedCpuTimeRemaining)

		deadline = QDateTime()
		deadline.setTime_t(self.__reportDeadline)

		self.__wuNameLabel.setText(QString(self.tr("Workunit name: %1")).arg(self.__wuName))
		self.__reportDeadlineText.setText(deadline.toString(loc.dateTimeFormat(QLocale.ShortFormat)))
		self.__estimatedCpuTimeRemainingText.setText(self.__getTimeString(self.__estimatedCpuTimeRemaining))

		try:
			activeTask = result['active_task']
			self.__fractionDone = float(activeTask['fraction_done'])
			self.__currentCpuTime = int(float(activeTask['current_cpu_time']))

			self.__fractionDoneText.setText(QString('%1').arg(round(self.__fractionDone * 100.0, 3))+ '%')
			self.__currentCpuTimeText.setText(self.__getTimeString(self.__currentCpuTime))
			self.__progressBar.setValue(int(self.__fractionDone * 10000.0))
			self.__activeTaskInfoGBox.show()
		except KeyError:
			self.__activeTaskInfoGBox.hide()
