import select
import socket
import sys
import errno
from HTMLParser import HTMLParser
from Debug import Debug
from WebServerConfig import WebServerConfig
from ErrorResponseCodes import ErrorResponseCodes
from FileServer import FileServer


class Poller:
    """ Polling server """
    def __init__(self,port, debug):
        self.host = ""
        self.port = port
        self.open_socket()
        self.clients = {}
        self.size = 10000
        self.debug = Debug(debug)
        self.cache = {}
        self.webServerConfig = WebServerConfig("web.conf", debug)
        self.timeOutTime = self.webServerConfig.getTimeOutTime()

        self.debug.printMessage("Hi!  This is a debug message")
        self.debug.printMessage("Hello, this is another message")

    def open_socket(self):
        """ Setup the socket for incoming clients """
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
            self.server.bind((self.host,self.port))
            self.server.listen(5)
        except socket.error, (value,message):
            if self.server:
                self.server.close()
            print "Could not open socket: " + message
            sys.exit(1)

    def run(self):
        """ Use poll() to handle each incoming client."""
        self.poller = select.epoll()
        self.pollmask = select.EPOLLIN | select.EPOLLHUP | select.EPOLLERR
        self.poller.register(self.server,self.pollmask)
        while True:
            # poll sockets
            try:
                fds = self.poller.poll(timeout=self.timeOutTime)
            except:
                return
            for (fd,event) in fds:
                # handle errors
                if event & (select.POLLHUP | select.POLLERR):
                    self.handleError(fd)
                    continue
                # handle the server socket
                if fd == self.server.fileno():
                    self.handleServer()
                    continue
                # handle client socket
                result = self.handleClient(fd)

    def handleError(self,fd):
        self.poller.unregister(fd)
        if fd == self.server.fileno():
            # recreate server socket
            self.server.close()
            self.open_socket()
            self.poller.register(self.server,self.pollmask)
        else:
            # close the socket
            self.clients[fd].close()
            del self.clients[fd]

    def handleServer(self):
        (client,address) = self.server.accept()
        client.setblocking(0)
        self.cache[client.fileno()] = ""
        self.clients[client.fileno()] = client
        self.poller.register(client.fileno(),self.pollmask)

    def handleClient(self,fd):
        # still need to figure out this whole thing.
        # Look at the Google group and on the 
        # slides called "event-driven-architecture"
        parser = HTMLParser(self.debug.isDebug())
        fileServer = FileServer(self.webServerConfig, self.debug.isDebug)

        while(True):
            request = self.cache[fd]
            try:
                data = self.clients[fd].recv(self.size)
                if data:
                    request += data
                else:
                    self.poller.unregister(fd)
                    self.clients[fd].close()
                    del self.clients[fd]
                    break
            except socket.error, e:
                err = e.args[0]
                if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
                    break

            if request.find("\r\n\r\n"):
                response = ""
                if parser.parse(request):
                    self.debug.printMessage("Parsing Completed")
                    self.debug.printMessage(parser.printAll())
                    response = fileServer.getResponse(parser)
                else:
                    self.debug.printMessage("Parsing Failed")
                    errorCodes = ErrorResponseCodes()
                    response = errorCodes.get400()
                
                # may need to put a try except to send again if error
                self.debug.printMessage("Response: ")
                self.debug.printMessage(response)
                self.clients[fd].send(response)
                break
            else:
                self.cache[fd] = request

        #parser = HTMLParser(data, self.debug.isDebug())
        #parser.printAll()
        """
        if data:
            html = "<html><body><h1>200 OK</h1></body></html>\r\n\r\n"

            headers = "HTTP/1.0 200 OK\r\n"
            headers += "Date: Fri, 31 Dec 1999 23:59:59 GMT\r\n"
            headers += "Content-Type: text/html\r\n"
            headers += "Content-Length: %d\r\n" % html.__len__()
            headers += "\r\n"
            response = headers + html
            self.clients[fd].send(response)
        else:
            self.poller.unregister(fd)
            self.clients[fd].close()
            del self.clients[fd]
            """