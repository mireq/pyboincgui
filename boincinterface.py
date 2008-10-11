import socket
import sys
import xml.dom.minidom

class BoincInterface:
    "Pripojenie na boinc."

    __host = "127.0.0.1"
    __port = 31416
    __sock = None

    def __init__(self):
        pass

    def __del__(self):
        if not self.__sock is None:
            self.__sock.close()
            self.__sock = None
        pass

    def connect(self):
        "Inicializacia spojenia, v pripade uspechu vracia 0"
        try:
            self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error, msg:
            sys.stderr("Error %s\n" %msg[1])
            return -1
            
        try:
            self.__sock.connect((self.__host,  self.__port))
        except socket.error,  msg:
            sys.stderr("Error %s\n" %msg[1])
            return -2

        (doc,  boincGuiRpcRequestElement) = self.createRpcRequest();
        auth1Element = doc.createElement("auth1")
        boincGuiRpcRequestElement.appendChild(auth1Element)
        reply = self.sendData(doc.toxml())
        return 0

    def sendData(self, data):
        data = data + "\003"
        print(data)
        while len(data) > 0:
            ns = self.__sock.send(data)
            data = data[ns:]
        rec = self.__sock.recv(1024)
        string = rec
        while rec[-1] != "\003":
            rec = self.__sock.recv(1024)
            string = string + recv
        print(string)
        return string
        
    def createRpcRequest(self):
        doc = xml.dom.minidom.Document();
        boincGuiRpcRequestElement = doc.createElement("boinc_gui_rpc_request")
        doc.appendChild(boincGuiRpcRequestElement)
        return (doc,  boincGuiRpcRequestElement)
