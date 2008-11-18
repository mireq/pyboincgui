import sys
from xml.dom import minidom
from xml.dom import Node
import md5
from connection import Connection

class BoincCommException(Exception):
	pass

class BoincMissingElementException(Exception):
	pass

class dailyStatistics:
	day                = 0
	user_total_credit  = 0.0
	user_expavg_credit = 0.0
	host_total_credit  = 0.0
	host_expavg_credit = 0.0
	def __init__(self, day, user_total_credit, user_expavg_credit, host_total_credit, host_expavg_credit):
		self.day                = day
		self.user_total_credit  = user_total_credit
		self.user_expavg_credit = user_expavg_credit
		self.host_total_credit  = host_total_credit
		self.host_expavg_credit = host_expavg_credit
	def data(self, index):
		if index == 0:
			return self.user_total_credit
		elif index == 1:
			return self.user_expavg_credit
		elif index == 2:
			return self.host_total_credit
		elif index == 3:
			return self.host_expavg_credit

class Interface:
	"Pripojenie na boinc."

	__host = None
	__port = None
	__conn = None
	__password = None
	__queue = None

	__connStateFunc = None

	unauthorized = -1
	disconnected = 0
	connecting   = 1
	connected    = 2

	__stateData = None

	def __init__(self,  host = "127.0.0.1",  port = 31416,  password = None, queue = None):
		self.__host = str(host)
		self.__port = port
		self.__password = str(password)
		self.__queue = queue

	def disconnect(self):
		self.__connStateFunc = None;
		self.__conn.disconnect()
		self.__queue = None;
		self.__conn = None

	def boincConnect(self, connStateFunc = None):
		self.__connStateFunc = connStateFunc
		if not self.__connStateFunc is None:
			self.__connStateFunc(self.disconnected)

		self.__conn = Connection(self.__host,  self.__port, self.__queue, self.__connStateChanged)
		self.__connStateFunc(self.connecting)

		(doc,  boincGuiRpcRequestElement) = self.createRpcRequest();
		auth1Element = doc.createElement("auth1")
		boincGuiRpcRequestElement.appendChild(auth1Element)
		self.__conn.sendData(doc.toxml(),  self.auth1)
		doc.unlink()

	def __connStateChanged(self, info):
		if isinstance(info, Exception):
			self.__queue.put(info)
			self.__connStateFunc(0)
		else:
			self.__connStateFunc(info)

	def __xmlToDict(self, node):
		slovnik = {}
		childNodes = node.childNodes;
		if childNodes.length == 1 and childNodes[0].nodeType == Node.TEXT_NODE:
			return childNodes[0].nodeValue

		for n in childNodes:
			if n.nodeType == Node.ELEMENT_NODE:
				try:
					if type(slovnik[n.nodeName]) == type([]):
						slovnik[n.nodeName].append(self.__xmlToDict(n))
					else:
						val = slovnik[n.nodeName]
						slovnik[n.nodeName] = [val, self.__xmlToDict(n)]
				except KeyError:
					slovnik[n.nodeName] = self.__xmlToDict(n)
		return slovnik

	def createRpcRequest(self):
		doc = minidom.Document();
		boincGuiRpcRequestElement = doc.createElement("boinc_gui_rpc_request")
		doc.appendChild(boincGuiRpcRequestElement)
		return (doc,  boincGuiRpcRequestElement)

	def getReply(self,  data):
		dataDom = minidom.parseString(data)
		reply = dataDom.documentElement
		if reply.nodeName != "boinc_gui_rpc_reply":
			raise BoincCommException("boinc_gui_rpc_reply not found")
		return (dataDom, reply)

	def auth1(self,  data):
		dom, reply = self.getReply(data)
		nonceNodes = reply.getElementsByTagName("nonce")
		if nonceNodes.length != 1:
			dom.unlink()
			raise BoincCommException("nonce not found")
		nonceNode = nonceNodes[0]
		nonce = nonceNode.childNodes[0].data
		reply = md5.new(nonce+self.__password).hexdigest()
		(doc,  boincGuiRpcRequestElement) = self.createRpcRequest();
		auth2Element = doc.createElement("auth2")
		boincGuiRpcRequestElement.appendChild(auth2Element)
		nHashElement = doc.createElement("nonce_hash")
		auth2Element.appendChild(nHashElement)
		nHText = doc.createTextNode(reply)
		nHashElement.appendChild(nHText)
		self.__conn.sendData(doc.toxml(),  self.auth2)
		dom.unlink()
		doc.unlink()

	def auth2(self, data):
		dom, reply = self.getReply(data)
		authNodes = reply.getElementsByTagName("authorized")
		if authNodes.length != 1:
			self.__connStateFunc(self.unauthorized)
			dom.unlink()
			raise BoincCommException("unauthorized")
		else:
			if not self.__connStateFunc is None:
				self.__connStateFunc(self.connected)
		dom.unlink()


	def __recvXml(self, data, tag, call = None):
		dom, reply = self.getReply(data)
		nodes = reply.getElementsByTagName(tag)
		if nodes.length != 1:
			dom.unlink()
			raise BoincCommException(tag)
		node = nodes[0]
		data = self.__xmlToDict(node)
		if call is None:
			dom.unlink()
			return data
		else:
			call(data)
		dom.unlink()

	def get_state(self, callback = None):
		self.__conn.sendData("<?xml version=\"1.0\" ?><boinc_gui_rpc_request><get_state /></boinc_gui_rpc_request>", self.__recvState, callback)

	def __recvState(self, data, call = None):
		dom, reply = self.getReply(data)
		clientStateNodes = reply.getElementsByTagName("client_state")
		if clientStateNodes.length != 1:
			dom.unlink()
			raise BoincCommException("client_state")
		clientState = clientStateNodes[0]
		self.__stateData = self.__xmlToDict(clientState)
		if not call is None:
			call(self.__stateData)
		dom.unlink()

	def get_project_status(self, callback = None):
		self.__conn.sendData("<?xml version=\"1.0\" ?><boinc_gui_rpc_request><get_project_status /></boinc_gui_rpc_request>", self.__recvProjects, callback)

	def __recvProjects(self, data, call = None):
		dom, reply = self.getReply(data)
		projectsNodes = reply.getElementsByTagName("projects")
		if projectsNodes.length != 1:
			dom.unlink()
			raise BoincCommException("projects")
		projectNode = projectsNodes[0]
		data = []
		for node in projectNode.childNodes:
			if node.nodeType == Node.ELEMENT_NODE:
				data.append(self.__xmlToDict(node))
		if not call is None:
			call(data)
		dom.unlink()

	def get_statistics(self, callback = None):
		self.__conn.sendData("<?xml version=\"1.0\" ?><boinc_gui_rpc_request><get_statistics /></boinc_gui_rpc_request>", self.__recvStatistics, callback)

	def __recvStatistics(self, data, call = None):
		out = {}
		dom, reply = self.getReply(data)
		statisticNode = reply.getElementsByTagName('statistics')[0]
		statisticsNodes = statisticNode.getElementsByTagName("project_statistics")
		for statistic in statisticsNodes:
			master_url = statistic.getElementsByTagName("master_url")[0].firstChild.data
			out[master_url] = []
			dailyStatisticsNodes = statistic.getElementsByTagName("daily_statistics")
			for dailyStatisticsNode in dailyStatisticsNodes:
				data = self.__xmlToDict(dailyStatisticsNode)
				out[master_url].append(dailyStatistics(int(float(data['day'])), float(data['user_total_credit']), float(data['user_expavg_credit']), float(data['host_total_credit']), float(data['host_expavg_credit'])))
		dom.unlink()
		if not call is None:
			call(out)
