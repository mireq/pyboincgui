from infoWidget import infoWidget
from PyQt4.QtCore import Qt, SIGNAL
from PyQt4.QtGui import QAction, QLabel, QGridLayout, QGroupBox, QHBoxLayout, QToolButton, QMenu, QPushButton
from BoincGui.titleframe import titleFrame
from os import execlp, fork
from platform import system
import os

class urlAction(QAction):
	__url = ""
	def __init__(self, url, name, description, parent):
		QAction.__init__(self, name, parent)
		self.setToolTip(description)
		self.setStatusTip(description)
		self.__url = url
		self.connect(self, SIGNAL("triggered()"), self.openUrl)

	def openUrl(self):
		pid = fork()
		if pid == 0:
			s = system()
			if os.name == 'mac':
				execlp('open', 'open', self.__url)
			if s == "Windows":
				execlp('start', 'start', self.__url)
			else:
				execlp('xdg-open', 'xdg-open', self.__url)

class projectInfoWidget(infoWidget):
	__master_url = ""
	__projectCached = None

	__mainLayout = None

	__projectInfo = None
	__projectInfoLayout = None
	__projectSettings = None

	#informacie o projekte
	__masterUrlLabel       = None
	__masterUrlText        = None
	__projectNameLabel     = None
	__projectNameText      = None
	__userNameLabel        = None
	__userNameText         = None
	__teamNameLabel        = None
	__teamNameText         = None
	__userTotalCreditLabel = None
	__userTotalCreditText  = None
	__hostTotalCreditLabel = None
	__hostTotalCreditText  = None
	__suspendedLabel       = None
	__newTasksLabel        = None

	__projectLinksButton = None
	__projectSettingsMenu   = None

	def __init__(self, client, project, parent = None):
		infoWidget.__init__(self, client, parent)

		self.__mainLayout = QGridLayout()
		self.__mainLayout.setRowStretch(1, 1)
		self.setMainLayout(self.__mainLayout)

		self.__projectInfo = QGroupBox(self.tr("Project Info"));
		self.__projectInfoLayout = QGridLayout()
		self.__projectInfo.setLayout(self.__projectInfoLayout)

		self.__projectSettings = QHBoxLayout()
		self.__projectLinksButton = QToolButton()
		self.__projectLinksButton.setText(self.tr("Project Links"))
		self.__projectLinksButton.hide()

		self.__updateProjectButton  = QPushButton(self.tr("Update"))
		self.__suspendProjectButton = QPushButton()
		self.__allowNewTasksButton  = QPushButton()
		self.__resetProjectButton   = QPushButton(self.tr("Reset project"))
		self.__detachProjectButton  = QPushButton(self.tr("Detach project"))

		self.__resetProjectButton.setEnabled(False)
		self.__detachProjectButton.setEnabled(False)

		self.__updateProjectButton.hide()
		self.__suspendProjectButton.hide()
		self.__allowNewTasksButton.hide()
		self.__resetProjectButton.hide()
		self.__detachProjectButton.hide()

		self.connect(self.__updateProjectButton, SIGNAL('clicked()'), self.__updateProject)
		self.connect(self.__suspendProjectButton, SIGNAL('clicked()'), self.__suspendProject)
		self.connect(self.__allowNewTasksButton, SIGNAL('clicked()'), self.__allowNewTasksProject)

		self.__projectSettings.addWidget(self.__projectLinksButton)
		self.__projectSettings.addWidget(self.__updateProjectButton)
		self.__projectSettings.addWidget(self.__suspendProjectButton)
		self.__projectSettings.addWidget(self.__allowNewTasksButton)
		#self.__projectSettings.addStretch(1)

		self.__projectAdmin = QHBoxLayout()
		self.__projectAdmin.addWidget(self.__resetProjectButton)
		self.__projectAdmin.addWidget(self.__detachProjectButton)
		#self.__projectAdmin.addStretch(1)

		self.__mainLayout.addWidget(self.__projectInfo, 0, 0)
		self.__mainLayout.addLayout(self.__projectSettings, 2, 0)
		self.__mainLayout.addLayout(self.__projectAdmin, 3, 0)

		self.__masterUrlLabel       = QLabel(self.tr("Master URL"))
		self.__projectNameLabel     = QLabel(self.tr("Project Name"))
		self.__userNameLabel        = QLabel(self.tr("User Name"))
		self.__teamNameLabel        = QLabel(self.tr("Team Name"))
		self.__userTotalCreditLabel = QLabel(self.tr("Total User Credits"))
		self.__hostTotalCreditLabel = QLabel(self.tr("Total Host Credits"))
		self.__suspendedLabel       = QLabel(self.tr("Suspended by user"))
		self.__newTasksLabel        = QLabel(self.tr("Won't get new tasks"))

		self.__masterUrlText       = QLabel()
		self.__projectNameText     = QLabel()
		self.__userNameText        = QLabel()
		self.__teamNameText        = QLabel()
		self.__userTotalCreditText = QLabel()
		self.__hostTotalCreditText = QLabel()

		self.__masterUrlText.setTextFormat(Qt.PlainText)
		self.__projectNameText.setTextFormat(Qt.PlainText)
		self.__userNameText.setTextFormat(Qt.PlainText)
		self.__teamNameText.setTextFormat(Qt.PlainText)
		self.__userTotalCreditText.setTextFormat(Qt.PlainText)
		self.__hostTotalCreditText.setTextFormat(Qt.PlainText)

		self.__masterUrlLabel.hide()
		self.__projectNameLabel.hide()
		self.__userNameLabel.hide()
		self.__teamNameLabel.hide()
		self.__userTotalCreditLabel.hide()
		self.__hostTotalCreditLabel.hide()

		self.__masterUrlText.hide()
		self.__projectNameText.hide()
		self.__userNameText.hide()
		self.__teamNameText.hide()
		self.__userTotalCreditText.hide()
		self.__hostTotalCreditText.hide()
		self.__suspendedLabel.hide()
		self.__newTasksLabel.hide()

		self.__projectInfoLayout.addWidget(self.__masterUrlLabel,        0, 0)
		self.__projectInfoLayout.addWidget(self.__projectNameLabel,      1, 0)
		self.__projectInfoLayout.addWidget(self.__userNameLabel,         2, 0)
		self.__projectInfoLayout.addWidget(self.__teamNameLabel,         3, 0)
		self.__projectInfoLayout.addWidget(self.__userTotalCreditLabel, 4, 0)
		self.__projectInfoLayout.addWidget(self.__hostTotalCreditLabel, 5, 0)

		self.__projectInfoLayout.addWidget(self.__masterUrlText,        0, 1)
		self.__projectInfoLayout.addWidget(self.__projectNameText,      1, 1)
		self.__projectInfoLayout.addWidget(self.__userNameText,         2, 1)
		self.__projectInfoLayout.addWidget(self.__teamNameText,         3, 1)
		self.__projectInfoLayout.addWidget(self.__userTotalCreditText, 4, 1)
		self.__projectInfoLayout.addWidget(self.__hostTotalCreditText, 5, 1)
		self.__projectInfoLayout.addWidget(self.__suspendedLabel, 6, 0, 1, 2)
		self.__projectInfoLayout.addWidget(self.__newTasksLabel, 7, 0, 1, 2)

		self.__master_url = project.data(0, Qt.UserRole + 1).toString()
		self.__projectCached = None

		self.__projectSettingsMenu = QMenu()
		self.__projectLinksButton.setPopupMode(QToolButton.InstantPopup)
		self.__projectLinksButton.setMenu(self.__projectSettingsMenu)

		projects = client.projectState()
		if not projects is None:
			self.updateProjects(projects)
		self.connect(client, SIGNAL("projectState(PyQt_PyObject)"), self.updateProjects)
		self.connect(client, SIGNAL("projectUpdateRecv(PyQt_PyObject)"), self.__updateProjectRecv)
		self.connect(client, SIGNAL("projectSuspendRecv(PyQt_PyObject)"), self.__suspendProjectRecv)
		self.connect(client, SIGNAL("projectResumeRecv(PyQt_PyObject)"), self.__resumeProjectRecv)
		self.connect(client, SIGNAL("projectNomoreworkRecv(PyQt_PyObject)"), self.__nomoreworkProjectRecv)
		self.connect(client, SIGNAL("projectAllowmoreworkRecv(PyQt_PyObject)"), self.__allowmoreworkProjectRecv)

	def __updateProject(self):
		self.emit(SIGNAL("showStatusBarMsg(QString)"), self.tr("Updating project"))
		self.client().projectUpdate(self.__projectCached['master_url'])

	def __suspendProject(self):
		if self.__projectCached['suspended_via_gui']:
			self.emit(SIGNAL("showStatusBarMsg(QString)"), self.tr("Resuming project"))
			self.client().projectResume(self.__projectCached['master_url'])
		else:
			self.emit(SIGNAL("showStatusBarMsg(QString)"), self.tr("Suspending project"))
			self.client().projectSuspend(self.__projectCached['master_url'])

	def __allowNewTasksProject(self):
		if self.__projectCached['dont_request_more_work']:
			self.emit(SIGNAL("showStatusBarMsg(QString)"), self.tr("Allowing new tasks"))
			self.client().projectAllowmorework(self.__projectCached['master_url'])
		else:
			self.emit(SIGNAL("showStatusBarMsg(QString)"), self.tr("Disallowing new tasks"))
			self.client().projectNomorework(self.__projectCached['master_url'])

	def __updateProjectRecv(self, status):
		if status:
			self.emit(SIGNAL("showStatusBarMsg(QString)"), status)
		else:
			self.emit(SIGNAL("showStatusBarMsg(QString)"), self.tr("Project updated"))
		self.client().getState()

	def __suspendProjectRecv(self, status):
		if status:
			self.emit(SIGNAL("showStatusBarMsg(QString)"), status)
		else:
			self.emit(SIGNAL("showStatusBarMsg(QString)"), self.tr("Project suspended"))
			self.__projectCached['suspended_via_gui'] = 1
			self.__suspendedLabel.show()
			self.__suspendProjectButton.setText(self.tr("Resume"))

		self.client().getState()

	def __resumeProjectRecv(self, status):
		if status:
			self.emit(SIGNAL("showStatusBarMsg(QString)"), status)
		else:
			self.emit(SIGNAL("showStatusBarMsg(QString)"), self.tr("Project restored"))
			self.__projectCached['suspended_via_gui'] = 0
			self.__suspendedLabel.hide()
			self.__suspendProjectButton.setText(self.tr("Suspend"))

		self.client().getState()

	def __nomoreworkProjectRecv(self, status):
		if status:
			self.emit(SIGNAL("showStatusBarMsg(QString)"), status)
		else:
			self.emit(SIGNAL("showStatusBarMsg(QString)"), self.tr("New tasks disallowed"))
			self.__projectCached['dont_request_more_work'] = 1
			self.__newTasksLabel.show()
			self.__allowNewTasksButton.setText(self.tr("Allow new tasks"))

		self.client().getState()

	def __allowmoreworkProjectRecv(self, status):
		if status:
			self.emit(SIGNAL("showStatusBarMsg(QString)"), status)
		else:
			self.emit(SIGNAL("showStatusBarMsg(QString)"), self.tr("New tasks allowed"))
			self.__projectCached['dont_request_more_work'] = 0
			self.__newTasksLabel.hide()
			self.__allowNewTasksButton.setText(self.tr("No new tasks"))

		self.client().getState()

	def __changeLabels(self, project, key, label, text):
		try:
			inf = project[key]
			if type(inf) == type(u""):
				text.setText(inf)
				text.show()
				label.show()
		except KeyError:
			text.hide()
			label.hide()

	def updateProjects(self, projects):
		projects = projects['project']
		project = None

		for proj in projects:
			if proj['master_url'] == self.__master_url:
				project = proj
				break

		# ak sme nenasli projekt
		if project is None:
			return

		if project != self.__projectCached:
			self.__projectCached = project
			try:
				self.setTitle(titleFrame(project['project_name']))
			except KeyError:
				pass

			self.__changeLabels(project, 'master_url', self.__masterUrlLabel, self.__masterUrlText)
			self.__changeLabels(project, 'project_name', self.__projectNameLabel, self.__projectNameText)
			self.__changeLabels(project, 'user_name', self.__userNameLabel, self.__userNameText)
			self.__changeLabels(project, 'team_name', self.__teamNameLabel, self.__teamNameText)
			self.__changeLabels(project, 'user_total_credit', self.__userTotalCreditLabel, self.__userTotalCreditText)
			self.__changeLabels(project, 'host_total_credit', self.__hostTotalCreditLabel, self.__hostTotalCreditText)

			if project['suspended_via_gui']:
				self.__suspendProjectButton.setText(self.tr("Resume"))
				self.__suspendedLabel.show()
			else:
				self.__suspendProjectButton.setText(self.tr("Suspend"))
				self.__suspendedLabel.hide()

			if project['dont_request_more_work']:
				self.__allowNewTasksButton.setText(self.tr("Allow new tasks"))
				self.__newTasksLabel.show()
			else:
				self.__allowNewTasksButton.setText(self.tr("No new tasks"))
				self.__newTasksLabel.hide()

			self.__updateProjectButton.show()
			self.__suspendProjectButton.show()
			self.__allowNewTasksButton.show()
			self.__resetProjectButton.show()
			self.__detachProjectButton.show()

			try:
				self.__projectSettingsMenu.clear()
				guiUrls = project['gui_urls']['gui_url']

				if type(guiUrls) == type({}):
					self.__projectSettingsMenu.addAction(urlAction(guiUrls['url'], guiUrls['name'], guiUrls['description'], self.__projectSettingsMenu))
				else:
					for url in guiUrls:
						self.__projectSettingsMenu.addAction(urlAction(url['url'], url['name'], url['description'], self.__projectSettingsMenu))

				try:
					ifTeamUrls = project['gui_urls']['ifteam']['gui_url']
					self.__projectSettingsMenu.addSeparator()
					if type(ifTeamUrls) == type({}):
						self.__projectSettingsMenu.addAction(urlAction(ifTeamUrls['url'], ifTeamUrls['name'], ifTeamUrls['description'], self.__projectSettingsMenu))
					else:
						for url in ifTeamUrls:
							self.__projectSettingsMenu.addAction(urlAction(url['url'], url['name'], url['description'], self.__projectSettingsMenu))
				except KeyError, msg:
					pass
				self.__projectLinksButton.show()
			except KeyError:
				self.__projectLinksButton.hide()
