import sys
import xml.dom.minidom
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

	def __del__(self):
		if not self.__conn is None:
			del self.__conn
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

	def createRpcRequest(self):
		doc = xml.dom.minidom.Document();
		boincGuiRpcRequestElement = doc.createElement("boinc_gui_rpc_request")
		doc.appendChild(boincGuiRpcRequestElement)
		return (doc,  boincGuiRpcRequestElement)

	def getReply(self,  data):
		dataDom = xml.dom.minidom.parseString(data)
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

	def get_state(self, callback):
		self.__conn.sendData("<?xml version=\"1.0\" ?><boinc_gui_rpc_request><get_state /></boinc_gui_rpc_request>", self.__recvState, callback)

	def __getNodeText(self, parent, nodeName):
		pass

	def __recvState(self, data, call = None):
		print(data)
		reply = self.getReply(data)
		clientStateNodes = reply.getElementsByTagName("client_state")
		if clientStateNodes.length != 1:
			raise BoncCommException("client_state")
		clientState = clientStateNodes[0]
		self.__stateData = {}
		host_info = clientState.getElementsByTagName('host_info')
		if host_info.length != 1:
			raise BoincMissingElementException('host_info')
		self.__stateData['host_info'] = {}