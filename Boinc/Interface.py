import socket
import sys
import xml.dom.minidom
from Connection import Connection

class Interface:
    "Pripojenie na boinc."

    __host = "127.0.0.1"
    __port = 31416
    __conn = None

    def __init__(self):
        self.__conn = Connection(self.__host,  self.__port)
        pass

    def __del__(self):
        if not self.__conn is None:
            del self.__conn
            self.__conn = None
        pass

    def connect(self):
        (doc,  boincGuiRpcRequestElement) = self.createRpcRequest();
        auth1Element = doc.createElement("auth1")
        boincGuiRpcRequestElement.appendChild(auth1Element)
        reply = self.__conn.sendData(doc.toxml())
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
