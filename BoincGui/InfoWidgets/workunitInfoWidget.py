from infoWidget import infoWidget
from PyQt4.QtGui import QGridLayout, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QGroupBox, QPushButton, QMessageBox
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
	__resultName = ''
	__projectUrl = ''
	__estimatedCpuTimeRemaining = 0
	__reportDeadline = 0

	#len aktivne
	__fractionDone = 0.0
	__currentCpuTime = 0

	__supprotGraphic = False
	__suspViaGui = False

	def __init__(self, client, project, workunit, parent = None):
		infoWidget.__init__(self, client, parent)

		self.__mainLayout = QVBoxLayout()
		self.setMainLayout(self.__mainLayout)

		self.__wuNameLabel                    = QLabel()
		self.__reportDeadlineLabel            = QLabel(self.tr("Report deadline:"))
		self.__estimatedCpuTimeRemainingLabel = QLabel(self.tr("Estimated CPU time remaining:"))
		self.__resultStateLabel               = QLabel(self.tr("State:"))
		self.__fractionDoneLabel              = QLabel(self.tr("Fraction done:"))
		self.__currentCpuTimeLabel            = QLabel(self.tr("Current CPU time:"))
		self.__processStateLabel              = QLabel(self.tr("Process state:"))

		self.__reportDeadlineText            = QLabel()
		self.__estimatedCpuTimeRemainingText = QLabel()
		self.__resultStateText               = QLabel()
		self.__fractionDoneText              = QLabel()
		self.__currentCpuTimeText            = QLabel()
		self.__processStateText              = QLabel()

		self.__progressBar = QProgressBar()
		self.__progressBar.setMaximum(10000);

		self.__actionsLayout = QHBoxLayout()
		self.__showGraphicsButton = QPushButton(self.tr("Show graphics"))
		self.__suspendButton = QPushButton()
		self.__abortButton = QPushButton(self.tr("Abort"))
		self.__actionsLayout.addWidget(self.__showGraphicsButton)
		self.__actionsLayout.addWidget(self.__suspendButton)
		self.__actionsLayout.addWidget(self.__abortButton)
		self.connect(self.__showGraphicsButton, SIGNAL('clicked()'), self.__showGraphics)
		self.connect(self.__suspendButton, SIGNAL('clicked()'), self.__suspend)
		self.connect(self.__abortButton, SIGNAL('clicked()'), self.__abort)

		self.__wuNameLabel.setTextFormat(Qt.PlainText)
		self.__estimatedCpuTimeRemainingLabel.setTextFormat(Qt.PlainText)
		self.__resultStateLabel.setTextFormat(Qt.PlainText)
		self.__reportDeadlineLabel.setTextFormat(Qt.PlainText)
		self.__fractionDoneLabel.setTextFormat(Qt.PlainText)
		self.__currentCpuTimeLabel.setTextFormat(Qt.PlainText)
		self.__processStateLabel.setTextFormat(Qt.PlainText)

		self.__reportDeadlineText.setTextFormat(Qt.PlainText)
		self.__estimatedCpuTimeRemainingText.setTextFormat(Qt.PlainText)
		self.__resultStateText.setTextFormat(Qt.PlainText)
		self.__fractionDoneText.setTextFormat(Qt.PlainText)
		self.__currentCpuTimeText.setTextFormat(Qt.PlainText)
		self.__processStateText.setTextFormat(Qt.PlainText)

		self.__wuNameLabel.setWordWrap(True)
		self.__estimatedCpuTimeRemainingLabel.setWordWrap(True)
		self.__resultStateLabel.setWordWrap(True)
		self.__reportDeadlineLabel.setWordWrap(True)
		self.__fractionDoneLabel.setWordWrap(True)
		self.__currentCpuTimeLabel.setWordWrap(True)
		self.__processStateLabel.setWordWrap(True)

		self.__reportDeadlineText.setWordWrap(True)
		self.__estimatedCpuTimeRemainingText.setWordWrap(True)
		self.__resultStateText.setWordWrap(True)
		self.__fractionDoneText.setWordWrap(True)
		self.__currentCpuTimeText.setWordWrap(True)
		self.__processStateText.setWordWrap(True)

		self.__taskInfoGBox = QGroupBox(self.tr("Task info"))
		self.__activeTaskInfoGBox = QGroupBox(self.tr("Process info"))

		self.__taskInfoLayout = QGridLayout()
		self.__processInfoLayout = QGridLayout()

		self.__taskInfoGBox.setLayout(self.__taskInfoLayout)
		self.__activeTaskInfoGBox.setLayout(self.__processInfoLayout)

		self.__mainLayout.addWidget(self.__taskInfoGBox)
		self.__mainLayout.addWidget(self.__activeTaskInfoGBox)
		self.__mainLayout.addStretch(1)
		self.__mainLayout.addWidget(self.__progressBar)
		self.__mainLayout.addLayout(self.__actionsLayout)

		self.__taskInfoLayout.addWidget(self.__wuNameLabel, 0, 0, 1, 2)
		self.__taskInfoLayout.addWidget(self.__reportDeadlineLabel, 1, 0)
		self.__taskInfoLayout.addWidget(self.__estimatedCpuTimeRemainingLabel, 2, 0)
		self.__taskInfoLayout.addWidget(self.__resultStateLabel, 3, 0)
		self.__taskInfoLayout.addWidget(self.__reportDeadlineText, 1, 1)
		self.__taskInfoLayout.addWidget(self.__estimatedCpuTimeRemainingText, 2, 1)
		self.__taskInfoLayout.addWidget(self.__resultStateText, 3, 1)

		self.__processInfoLayout.addWidget(self.__fractionDoneLabel, 0, 0)
		self.__processInfoLayout.addWidget(self.__currentCpuTimeLabel, 1, 0)
		self.__processInfoLayout.addWidget(self.__processStateLabel, 2, 0)
		self.__processInfoLayout.addWidget(self.__fractionDoneText, 0, 1)
		self.__processInfoLayout.addWidget(self.__currentCpuTimeText, 1, 1)
		self.__processInfoLayout.addWidget(self.__processStateText, 2, 1)

		self.__masterURL = project.data(0, Qt.UserRole + 1).toString()
		self.__name = workunit.data(0, Qt.UserRole + 1).toString()

		projects = client.projectState()
		if not projects is None:
			self.updateProjects(projects)
		self.connect(client, SIGNAL("projectState(PyQt_PyObject)"), self.updateProjects)
		self.connect(client, SIGNAL('resultShowGraphicsRecv(PyQt_PyObject)'), self.__resultShowGraphicsRecv)
		self.connect(client, SIGNAL('suspendResultRecv(PyQt_PyObject)'), self.__suspendResultRecv)
		self.connect(client, SIGNAL('resumeResultRecv(PyQt_PyObject)'), self.__resumeResultRecv)
		self.connect(client, SIGNAL('abortResultRecv(PyQt_PyObject)'), self.__abortResultRecv)

	def __resultShowGraphicsRecv(self, status):
		if status:
			self.emit(SIGNAL("showStatusBarMsg(QString)"), status)
		else:
			self.emit(SIGNAL("showStatusBarMsg(QString)"), self.tr("Graphics displayed"))

	def __suspendResultRecv(self, status):
		if status:
			self.emit(SIGNAL("showStatusBarMsg(QString)"), status)
		else:
			self.emit(SIGNAL("showStatusBarMsg(QString)"), self.tr("Result suspended"))
			self.__suspViaGui = True
			self.__suspendButton.setText(self.tr('Resume'))
		self.client().getState()

	def __resumeResultRecv(self, status):
		if status:
			self.emit(SIGNAL("showStatusBarMsg(QString)"), status)
		else:
			self.emit(SIGNAL("showStatusBarMsg(QString)"), self.tr("Result restored"))
			self.__suspViaGui = False
			self.__suspendButton.setText(self.tr('Suspend'))
		self.client().getState()

	def __abortResultRecv(self, status):
		if status:
			self.emit(SIGNAL("showStatusBarMsg(QString)"), status)
		else:
			self.emit(SIGNAL("showStatusBarMsg(QString)"), self.tr("Result aborted"))

	def __showGraphics(self):
		self.client().resultShowGraphics(self.__projectUrl, self.__resultName)

	def __suspend(self):
		if self.__suspViaGui:
			self.emit(SIGNAL("showStatusBarMsg(QString)"), self.tr("Resuming result"))
			self.client().resumeResult(self.__projectUrl, self.__resultName)
		else:
			self.emit(SIGNAL("showStatusBarMsg(QString)"), self.tr("Suspending result"))
			self.client().suspendResult(self.__projectUrl, self.__resultName)

	def __abort(self):
		btn = QMessageBox.question(self, self.tr("Abort result"), self.tr("Are you sure that you want to abort result?"), QMessageBox.Yes|QMessageBox.No)
		if btn == QMessageBox.Yes:
			self.emit(SIGNAL("showStatusBarMsg(QString)"), self.tr("Aborting result"))
			self.client().abortResult(self.__projectUrl, self.__resultName)

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
		self.__resultName = result['name'];
		self.__projectUrl = result['project_url'];
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

		state = int(result['state'])
		if state == 0:
			stateText = self.tr("New")
		elif state == 1:
			stateText = self.tr("Input files for result are being downloaded")
		elif state == 2:
			try:
				activeTaskState = int(result['active_task']['active_task_state'])
				if activeTaskState == 1:
					stateText = self.tr("Files are downloaded, result is being computed")
				else:
					stateText = self.tr("Files are downloaded, result can be computed")
			except KeyError:
				stateText = self.tr("Files are downloaded, result can be computed")
		elif state == 3:
			stateText = self.tr("Computation failed")
		elif state == 4:
			stateText = self.tr("Output files for result are being uploaded")
		elif state == 5:
			stateText = self.tr("Files are uploaded")
		elif state == 6:
			stateText = self.tr("Result was aborted")
		else:
			stateText = self.tr("Unknown")

		self.__resultStateText.setText(stateText)

		try:
			activeTask = result['active_task']
			activeTaskState = int(activeTask['active_task_state'])

			if activeTaskState == 0:
				stateText = self.tr("Unitialized")
			elif activeTaskState == 1:
				stateText = self.tr("Running")
			elif (activeTaskState >= 2 and activeTaskState <= 4) or activeTaskState == 6:
				stateText = self.tr("Aborted")
			elif activeTaskState == 5:
				stateText = self.tr("Abort pending")
			elif activeTaskState == 7:
				stateText = self.tr("Process couldnt start")
			elif activeTaskState == 8:
				stateText = self.tr("Quit pending")
			elif activeTaskState == 9:
				stateText = self.tr("Suspended")
			else:
				stateText = self.tr("Unknown")

			self.__processStateText.setText(stateText)

			self.__fractionDone = float(activeTask['fraction_done'])
			self.__currentCpuTime = int(float(activeTask['current_cpu_time']))

			self.__fractionDoneText.setText(QString('%1').arg(round(self.__fractionDone * 100.0, 3))+ '%')
			self.__currentCpuTimeText.setText(self.__getTimeString(self.__currentCpuTime))
			self.__progressBar.setValue(int(self.__fractionDone * 10000.0))
			
			self.__activeTaskInfoGBox.show()

		except KeyError:
			self.__activeTaskInfoGBox.hide()

		# akcie s workunitom
		try:
			self.__suspViaGui = result['suspended_via_gui']
			self.__suspViaGui = True
		except KeyError:
			self.__suspViaGui = False

		if self.__suspViaGui:
			self.__suspendButton.setText(self.tr('Resume'))
		else:
			self.__suspendButton.setText(self.tr('Suspend'))

		# podpora grafiky
		try:
			self.__supportGraphic = result['active_task']['supports_graphics']
			self.__supportGraphic = True
			self.__showGraphicsButton.setEnabled(True)
		except KeyError:
			self.__supprotGraphic = False
			self.__showGraphicsButton.setEnabled(False)

		
