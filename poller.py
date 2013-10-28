import select
import socket
import sys
from HTMLParser import HTMLParser

class Poller:
    """ Polling server """
    def __init__(self,port, debug):
        self.host = ""
        self.port = port
        self.open_socket()
        self.clients = {}
        self.size = 1024
        self.debug = debug

        self.DEBUG("Hi!  This is a debug message")
        self.DEBUG("Hello, this is another message")

    def DEBUG(self,message):
        if self.debug:
            print message
        else:
            print "DEBUG disabled"

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
                fds = self.poller.poll(timeout=1)
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
                print "Got to here"
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
        self.clients[client.fileno()] = client
        self.poller.register(client.fileno(),self.pollmask)

    def handleClient(self,fd):
        data = self.clients[fd].recv(self.size)

        parser = HTMLParser(data)
        parser.printAll()

        if data:
            print "\"" + data + "\""
            html = "<html><body><h1>200 OK</h1></body></html>\r\n\r\n"

            headers = "HTTP/1.0 200 OK\r\n"
            headers += "Date: Fri, 31 Dec 1999 23:59:59 GMT\r\n"
            headers += "Content-Type: text/html\r\n"
            headers += "Content-Length: %d\r\n" % html.__len__()
            headers += "\n"
            response = headers + html
            self.clients[fd].send(response)
        else:
            self.poller.unregister(fd)
            self.clients[fd].close()
            del self.clients[fd]
