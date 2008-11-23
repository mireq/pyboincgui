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

	"""Stavy pripojenia"""
	unauthorized = -1
	disconnected = 0
	connecting   = 1
	connected    = 2

	__stateData = None

	def __init__(self,  host = "127.0.0.1",  port = 31416,  password = None, queue = None):
		"""
		Vytvorenie noveho rozhania pre pripojenie k systemu BOINC

		Pripojenie k hostovi (host) cez port (port) s heslom (password) a
		frontou pre chyby (queue). Pripojenie nie je automaticke.
		"""
		self.__host = str(host)
		self.__port = port
		self.__password = str(password)
		self.__queue = queue

	def disconnect(self):
		"""
		Odpojenie od klienta BOINC
		"""
		self.__connStateFunc = None;
		self.__conn.disconnect()
		self.__queue = None;
		self.__conn = None

	def boincConnect(self, connStateFunc = None):
		"""
		Pripojenie ku klientovi BOINC

		Tato funkcia prijma ako argument referenciu na funkciu ktora
		sa vola pri zmene stavu pripojenia. Tato funkcia nic nevracia a moze
		skoncit este pred pripojenim. Preto je jediny sposob ako zistit
		stav pripojenia pouzitie connStateFunc.
		"""
		self.__connStateFunc = connStateFunc
		if not self.__connStateFunc is None:
			self.__connStateFunc(self.disconnected)

		self.__conn = Connection(self.__host,  self.__port, self.__queue, self.__connStateChanged)
		self.__connStateFunc(self.connecting)

		(doc,  boincGuiRpcRequestElement) = self.createRpcRequest();
		auth1Element = doc.createElement("auth1")
		boincGuiRpcRequestElement.appendChild(auth1Element)
		self.__conn.sendData(doc.toxml(),  self.__auth1)
		doc.unlink()

	def __connStateChanged(self, info):
		"""
		Zmena stavu pripojenia
		"""
		if isinstance(info, Exception):
			self.__queue.put(info)
			self.__connStateFunc(0)
		else:
			self.__connStateFunc(info)

	def __xmlToDict(self, node):
		"""
		Konverzia xml DOM uzla na slovnik
		"""
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

	def __getReplyState(self, reply):
		"""
		Funkcia pre ziskanie informacii uspesnosti volania poziadavky

		Po uspesnom volani vracia False, inac vracia text chyby. Tato funkcia
		sa da pouzit len pre prijate v tvare
		<boinc_gui_rpc_reply>
		  <sucess /> alebo <error>sprava o chybe</error>
		</boinc_gui_rpc_reply>
		"""
		if len(reply.getElementsByTagName('success')) > 0:
			return False
		else:
			errorNodes = reply.getElementsByTagName('error')
			if len(errorNodes) > 0:
				return self.__getText(errorNodes[0])

	def createRpcRequest(self):
		"""
		Vytvorenie dom pre request

		Vsetky requesty maju tvar
		<boinc_gui_rpc_request></boinc_gui_rpc_request>
		Tatp funkcia vytvori prave taku strukturu a vracia objekt typu tuple
		s polozkamy DOM a uzol boinc_gui_rpc_request. DOM je nutne rucne
		dealokovat pomocou metody unlink().
		"""
		doc = minidom.Document();
		boincGuiRpcRequestElement = doc.createElement("boinc_gui_rpc_request")
		doc.appendChild(boincGuiRpcRequestElement)
		return (doc,  boincGuiRpcRequestElement)

	def getReply(self,  data):
		"""
		Vytiahnutie elementy boinc_gui_rpc_reply z retazca

		Navratovou hodnotou je DOM a uzol boinc_gui_rpc_reply. DOM je nutne
		rucne dealokovat pomocou metody unlink().
		"""
		dataDom = minidom.parseString(data)
		reply = dataDom.documentElement
		if reply.nodeName != "boinc_gui_rpc_reply":
			raise BoincCommException("boinc_gui_rpc_reply not found")
		return (dataDom, reply)

	def __auth1(self,  data):
		"""
		Prva faza autorizacie - poslanie prihlasovacich udajov
		"""
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

		self.__conn.sendData(doc.toxml(),  self.__auth2)

		dom.unlink()
		doc.unlink()

	def __auth2(self, data):
		"""
		Druha faza autorizacie - prijatie informacie o uspesnosti autorizacie
		"""
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
		"""
		Spracovanie stringu(data), vytiahnutie tagu, prevod na dict, volanie call
		"""
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
		"""
		Zistenie stavu klienta, projektov a workunitov
		"""
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
		"""
		Zistenie stavu projektov
		"""
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
		"""
		Ziskanie statistik (pre rozne grafy)

		Vysledok je slovnik ktoreho klucom je URL projektu a hodnotou
		je pole objektov dailyStatistics
		"""
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

	def get_file_transfers(self, callback = None):
		"""
		Ziskanie infomacii o prenosoch suborov

		Navratovou hodnotou je pole slovnikov. Jednotlive polozky slovnika
		zodpovedaju polozkam vo vysledku poziadavky. Chybajuce polia su
		doplnene na standardnu hodnotu (vacsinou 0).
		"""
		self.__conn.sendData("<?xml version=\"1.0\" ?><boinc_gui_rpc_request><get_file_transfers /></boinc_gui_rpc_request>", self.__recvFileTransfers, callback)

	def __recvFileTransfers(self, data, call = None):
		out = []
		dom, reply = self.getReply(data)
		fileTransfersNode = reply.getElementsByTagName('file_transfers')[0]
		fileTransfers = fileTransfersNode.getElementsByTagName('file_transfer')
		for ftNode in  fileTransfers:
			fileTransfer = {}
			fileTransfer['name']                 = self.__getStr(ftNode, 'name')
			fileTransfer['project_url']          = self.__getStr(ftNode, 'project_url')
			fileTransfer['project_name']         = self.__getStr(ftNode, 'project_name')
			fileTransfer['nbytes']               = self.__getFloat(ftNode, 'nbytes')
			fileTransfer['generated_locally']    = self.__nodeExist(ftNode, 'generated_locally')
			fileTransfer['uploaded']             = self.__nodeExist(ftNode, 'uploaded')
			fileTransfer['upload_when_present']  = self.__nodeExist(ftNode, 'upload_when_present')
			fileTransfer['sticky']               = self.__nodeExist(ftNode, 'sticky')
			fileTransfer['persistent_file_xfer'] = self.__nodeExist(ftNode, 'persistent_file_xfer')
			fileTransfer['file_xfer']            = self.__nodeExist(ftNode, 'file_xfer')
			fileTransfer['num_retries']          = self.__getInt(ftNode, 'num_retries')
			fileTransfer['first_request_time']   = self.__getInt(ftNode, 'first_request_time')
			fileTransfer['next_request_time']    = self.__getInt(ftNode, 'next_request_time')
			fileTransfer['status']               = self.__getInt(ftNode, 'status')
			fileTransfer['time_so_far']          = self.__getFloat(ftNode, 'time_so_far')
			fileTransfer['last_bytes_xferred']   = self.__getFloat(ftNode, 'last_bytes_xferred')
			fileTransfer['file_offset']          = self.__getFloat(ftNode, 'file_offset')
			fileTransfer['xfer_speed']           = self.__getFloat(ftNode, 'xfer_speed')
			fileTransfer['host']                 = self.__getStr(ftNode, 'host')
			xferNodes = ftNode.getElementsByTagName('file_xfer')
			if len(xferNodes) == 1:
				xferNode = xferNodes[0]
				fileTransfer['bytes_xferred'] = self.__getFloat(xferNode, 'bytes_xferred')
				fileTransfer['file_offset']   = self.__getFloat(xferNode, 'file_offset')
				fileTransfer['xfer_speed']    = self.__getFloat(xferNode, 'xfer_speed')
				fileTransfer['url']           = self.__getStr(xferNode, 'url')
			else:
				fileTransfer['bytes_xferred'] = 0.0
				fileTransfer['file_offset']   = 0.0
				fileTransfer['xfer_speed']    = 0.0
				fileTransfer['url']           = ''
			out.append(fileTransfer)
		dom.unlink()
		call(out)

	def __getText(self, node):
		"""
		Ziskanie textu z netextoveho uzla ktory ma 1 potomka - TEXT_NODE
		"""
		childNodes = node.childNodes
		if len(childNodes) != 1:
			return None
		vysledokNode = childNodes[0]
		if vysledokNode.nodeType != Node.TEXT_NODE:
			return None
		return vysledokNode.nodeValue

	def __getStr(self, node, name):
		"""
		Ziskanie textu z potomka uzla (node) s menom (name).
		"""
		nodes = node.getElementsByTagName(name)
		if len(nodes) != 1:
			return None
		return self.__getText(nodes[0])

	def __getFloat(self, node, name):
		"""
		Ziskanie desatinneho cisla z potomka uzla (node) s menom (name).
		"""
		string = self.__getStr(node, name)
		if string is None:
			return None
		try:
			return float(string)
		except ValueError:
			return None

	def __getInt(self, node, name):
		"""
		Ziskanie celeho cisla z potomka uzla (node) s menom (name).
		"""
		string = self.__getStr(node, name)
		if string is None:
			return None
		try:
			return int(string)
		except ValueError:
			try:
				return int(float(string))
			except ValueError:
				return None
			return None

	def __nodeExist(self, node, name):
		"""
		Vracia true ak uzol (node) ma potomka s danym menom (name)
		"""
		nodes = node.getElementsByTagName(name)
		if len(nodes) > 0:
			return True
		else:
			return False

	def __add_text_node(self, dom, node, nodeName, text):
		"""
		Vytvorenie noveho uzla v node s menom nodeName a v nome text
		"""
		newNode = dom.createElement(nodeName)
		node.appendChild(newNode)

		textNode = dom.createTextNode(text)
		newNode.appendChild(textNode)

	# jednoduche akcie s projektom
	def __createProjectActionRequest(self, actionName, projectUrl):
		"""
		Vytvorenie jednoduchej akcie s projektom (ako update a pod.)
		"""
		(dom, request) = self.createRpcRequest()
		actionNode = dom.createElement(actionName)
		request.appendChild(actionNode)

		self.__add_text_node(dom, actionNode, 'project_url', projectUrl)

		request = dom.toxml()
		dom.unlink()
		return request

	def __recvActionState(self, data, callback = None):
		"""
		Prijatie stavu jednoduchej akcie
		"""
		dom, reply = self.getReply(data)
		state = self.__getReplyState(reply)
		dom.unlink()
		if not callback is None:
			callback(state)

	def project_update(self, project, callback = None):
		"""
		Aktualizacia projektu
		"""
		request = self.__createProjectActionRequest('project_update', project)
		self.__conn.sendData(request, self.__recvActionState, callback)

	def project_suspend(self, project, callback = None):
		"""
		Uspanie projektu
		"""
		request = self.__createProjectActionRequest('project_suspend', project)
		self.__conn.sendData(request, self.__recvActionState, callback)

	def project_resume(self, project, callback = None):
		"""
		Pokracovanie v projekte
		"""
		request = self.__createProjectActionRequest('project_resume', project)
		self.__conn.sendData(request, self.__recvActionState, callback)

	def project_nomorework(self, project, callback = None):
		"""
		Zakazanie novej roboty
		"""
		request = self.__createProjectActionRequest('project_nomorework', project)
		self.__conn.sendData(request, self.__recvActionState, callback)

	def project_allowmorework(self, project, callback = None):
		"""
		Povolenie novej roboty
		"""
		request = self.__createProjectActionRequest('project_allowmorework', project)
		self.__conn.sendData(request, self.__recvActionState, callback)

	# praca s workunitom

	def __addResultInfo(self, dom, node, url, name):
		"""
		Pridanie potrebnych informacii do uzlu (node) o workunite pre akcie s workunitom
		"""
		self.__add_text_node(dom, node, 'project_url', url)
		self.__add_text_node(dom, node, 'name', name)

	# grafika
	def result_show_graphics(self, url, name, typ = 'window', callback = None):
		"""
		Zobrazenie grafiky workunitu
		"""
		(dom, request) = self.createRpcRequest()
	
		resultShowGraphicsNode = dom.createElement('result_show_graphics')
		request.appendChild(resultShowGraphicsNode)

		self.__add_text_node(dom, resultShowGraphicsNode, 'project_url', url)
		self.__add_text_node(dom, resultShowGraphicsNode, 'result_name', name)

		resultShowGraphicsNode.appendChild(dom.createElement(typ))
		request = dom.toxml()
		dom.unlink()
		self.__conn.sendData(request, self.__recvActionState, callback)

	def suspend_result(self, url, name, callback = None):
		"""
		Uspanie workunitu
		"""
		(dom, request) = self.createRpcRequest()
	
		suspendResultNode = dom.createElement('suspend_result')
		request.appendChild(suspendResultNode)

		self.__addResultInfo(dom, suspendResultNode, url, name)
		request = dom.toxml()
		dom.unlink()
		self.__conn.sendData(request, self.__recvActionState, callback)

	def resume_result(self, url, name, callback = None):
		"""
		Pokracovanie v praci na workunite
		"""
		(dom, request) = self.createRpcRequest()
	
		resumeResultNode = dom.createElement('resume_result')
		request.appendChild(resumeResultNode)

		self.__addResultInfo(dom, resumeResultNode, url, name)
		request = dom.toxml()
		dom.unlink()
		self.__conn.sendData(request, self.__recvActionState, callback)

	def abort_result(self, url, name, callback = None):
		"""
		Ukoncenie workunitu
		"""
		(dom, request) = self.createRpcRequest()
	
		abortResultNode = dom.createElement('abort_result')
		request.appendChild(abortResultNode)

		self.__addResultInfo(dom, abortResultNode, url, name)
		request = dom.toxml()
		dom.unlink()
		self.__conn.sendData(request, self.__recvActionState, callback)
