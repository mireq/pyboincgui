import socket
import sys

class BoincConnectionException(Exception):
    pass

class Connection:
    """Pripojenie ku klientovi BOINC
    
    Tato trieda zabezpecuje len pripojenie ku klientovi.
    O veci ako autorizacia sa musi starat uzivatel tejto triedy."""
    
    __host = None
    __port = None
    __sock = None
    
    def __init__(self,  host,  port):
        self.__host = host
        self.__port = port
        try:
            self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error, msg:
            sys.stderr.write("Error %s\n" %msg[1])
            raise BoincConnectionException(msg[1])

        try:
            self.__sock.connect((self.__host,  self.__port))
        except socket.error,  msg:
            sys.stderr.write("Error %s\n" %msg[1])
            raise BoincConnectionException(msg[1])

    def __del__(self):
        if not self.__sock is None:
            self.__sock.close()
            self.__sock = None

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
