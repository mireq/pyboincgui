import sys
import xml.dom.minidom
import md5
from connection import Connection

class BoincCommException(Exception):
	pass

class Interface:
	"Pripojenie na boinc."

	__host = None
	__port = None
	__conn = None
	__password = None

	def __init__(self,  host = "127.0.0.1",  port = 31416,  password = None):
		self.__host = host
		self.__port = port
		self.__password = password
		pass

	def __del__(self):
		if not self.__conn is None:
			del self.__conn
			self.__conn = None
		pass

	def connect(self):
		self.__conn = Connection(self.__host,  self.__port)
		(doc,  boincGuiRpcRequestElement) = self.createRpcRequest();
		auth1Element = doc.createElement("auth1")
		boincGuiRpcRequestElement.appendChild(auth1Element)
		self.__conn.sendData(doc.toxml(),  self.auth1)

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
		self.__conn.sendData(doc.toxml(),  None)
		pass
