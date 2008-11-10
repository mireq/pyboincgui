import sys
from xml.dom import minidom
from xml.dom import Node
import md5
from connection import Connection

class BoincCommException(Exception):
	pass

class BoincMissingElementException(Exception):
	pass

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
		return reply

	def auth1(self,  data):
		reply = self.getReply(data)
		nonceNodes = reply.getElementsByTagName("nonce")
		if nonceNodes.length != 1:
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
		pass

	def auth2(self, data):
		reply = self.getReply(data)
		authNodes = reply.getElementsByTagName("authorized")
		if authNodes.length != 1:
			self.__connStateFunc(self.unauthorized)
			raise BoincCommException("unauthorized")
		else:
			if not self.__connStateFunc is None:
				self.__connStateFunc(self.connected)


	def __recvXml(self, data, tag, call = None):
		reply = self.getReply(data)
		nodes = reply.getElementsByTagName(tag)
		if nodes.length != 1:
			raise BoincCommException(tag)
		node = nodes[0]
		data = self.__xmlToDict(node)
		if call is None:
			return data
		else:
			call(data)

	def get_state(self, callback = None):
		self.__conn.sendData("<?xml version=\"1.0\" ?><boinc_gui_rpc_request><get_state /></boinc_gui_rpc_request>", self.__recvState, callback)

	def __recvState(self, data, call = None):
		reply = self.getReply(data)
		clientStateNodes = reply.getElementsByTagName("client_state")
		if clientStateNodes.length != 1:
			raise BoincCommException("client_state")
		clientState = clientStateNodes[0]
		self.__stateData = self.__xmlToDict(clientState)
		if not call is None:
			call(self.__stateData)

	def get_project_status(self, callback = None):
		self.__conn.sendData("<?xml version=\"1.0\" ?><boinc_gui_rpc_request><get_project_status /></boinc_gui_rpc_request>", self.__recvProjects, callback)

	def __recvProjects(self, data, call = None):
		reply = self.getReply(data)
		projectsNodes = reply.getElementsByTagName("projects")
		if projectsNodes.length != 1:
			raise BoincCommException("projects")
		projectNode = projectsNodes[0]
		data = []
		for node in projectNode.childNodes:
			if node.nodeType == Node.ELEMENT_NODE:
				data.append(self.__xmlToDict(node))
		if not call is None:
			call(data)
