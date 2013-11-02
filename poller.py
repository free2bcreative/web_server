import select
import socket
import sys
import errno
import time
from HTMLParser import HTMLParser
from Debug import Debug
from WebServerConfig import WebServerConfig
from ErrorResponseCodes import ErrorResponseCodes
from FileServer import FileServer


class Poller:
    """ Polling server """
    def __init__(self,port, debug):
        self.debug = Debug(debug)
        self.host = ""
        self.port = port
        self.open_socket()
        self.clients = {}
        self.last_used = {} # dictionary containing times a fd (socket) was last used
        self.sweepTime = 5.0 # how long before we sweep through sockets and close the ones that need closing
        self.size = 10000
        self.cache = {}
        self.webServerConfig = WebServerConfig("web.conf", debug)
        self.timeOutTime = self.webServerConfig.getTimeOutTime()

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
        
        # mark and sweep code
        self.lastChecked = time.time() # last time we swept through all of the sockets
        
        while True:
            # poll sockets
            try:
                fds = self.poller.poll(timeout=self.timeOutTime)
            except:
                return

            # mark and sweep code
            self.now = time.time()

            for (fd,event) in fds:
                # handle errors
                if event & (select.POLLHUP | select.POLLERR):
                    self.handleError(fd)
                    continue
                # handle the server socket
                if fd == self.server.fileno():
                    self.handleServer()
                    continue

                # mark and sweep code
                self.last_used[fd] = self.now



                # handle client socket
                result = self.handleClient(fd)

                # mark and sweep code
                if self.now - self.lastChecked > self.sweepTime:
                    self.debug.printMessage("Sweeping and deleting any clients not being used...")
                    for fileDescriptor in self.last_used:
                        self.debug.printMessage("Found fileDescriptor (%d) in self.clients. Checking..." % fileDescriptor)
                        if self.now - self.last_used[fileDescriptor] > self.sweepTime:
                            self.debug.printMessage("fileDescriptor was open for too long.  Closing socket...")

                            self.poller.unregister(fileDescriptor)
                            self.clients[fileDescriptor].close()
                            del self.clients[fileDescriptor]
                            del self.last_used[fileDescriptor]
                    self.lastChecked = self.now

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
            del self.last_used[fd]

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
        fileServer = FileServer(self.webServerConfig, self.debug.isDebug())

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
                    del self.last_used[fd]
                    break
            except socket.error, e:
                err = e.args[0]
                if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
                    break

            if request.find("\r\n\r\n"):
                response = ""
                if parser.parse(request):
                    self.debug.printMessage("Parsing Completed")
                    response = fileServer.getResponse(parser)

                else:
                    self.debug.printMessage("Parsing Failed")
                    errorCodes = ErrorResponseCodes()
                    response = errorCodes.get400()
                
                # Sending response
                while True:
                    try:
                        sentBytes = self.clients[fd].send(response)
                        break
                    except socket.error, e:
                        err = e.args[0]
                        if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
                            continue
                filePath = fileServer.getFilePath()
                if not filePath == "":
                    self.sendFile(self.clients[fd], filePath)

                break
            else:
                self.cache[fd] = request


    def sendFile(self, sock, filePath):
        file = open(filePath, "rb")
        
        chunk = file.read(10000)
        while chunk:
            
            totalsent = 0
            while totalsent < len(chunk):
                self.debug.printMessage("totalsent: %d\nchunkLength: %d" % (totalsent, len(chunk)))
                try:
                    sentBytes = sock.send(chunk[totalsent:])
                    self.debug.printMessage("Number of Bytes sent: %d" % sentBytes)
                except socket.error, e:
                    err = e.args[0]
                    if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
                        self.debug.printMessage("Encountered EAGAIN or EWOULDBLOCK. Trying again...")
                        continue
                totalsent += sentBytes
                self.debug.printMessage("totalsent: %d" % totalsent)

            chunk = file.read(10000)


        self.debug.printMessage("Finished sending file.  Closing file...")
        file.close()