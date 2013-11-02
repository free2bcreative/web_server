import os
from stat import *
import time
from Debug import Debug
from ErrorResponseCodes import ErrorResponseCodes

class FileServer:
	""" FileServer """
	def __init__(self, webServerConfig,debug):
		self.debug = Debug(debug)
		self.unimplementedRequestMethods = ['HEAD', 'POST', 'PUT', 'DELETE', 'LINK', 'UNLINK']
		self.webServerConfig = webServerConfig
		self.errorCodes = ErrorResponseCodes()
		self.filePath = ""

	def getResponse(self, htmlParser):
		self.filePath = ""

		# check if valid GET request
		self.debug.printMessage("Checking if valid GET request...")
		if not htmlParser.getMethod() == "GET":
			if htmlParser.getMethod() in self.unimplementedRequestMethods:
				return self.errorCodes.get501()
			return self.errorCodes.get400()

		# translate URI to filename
		self.debug.printMessage("Translating request to URL...")
		host = htmlParser.getHost()
		uri = htmlParser.getUri()
		filePath = self.webServerConfig.getPath(host) + uri
		if filePath[-1] == '/':
			filePath += "index.html"
		self.debug.printMessage("FilePath: " + filePath)

		# check if good filePath or no permissions given
		self.debug.printMessage("Checking if good filePath or no permissions given")
		try:
			f = open(filePath)
			self.debug.printMessage("Opened file just fine")
			self.filePath = filePath
		except IOError as (errno, strerror):
			if errno == 13:
				""" 403 Forbidden """
				return self.errorCodes.get403()
			elif errno == 2:
				""" 404 Not Found """
				return self.errorCodes.get404()
			else:
				""" 500 Internal Server Error """
				return self.errorCodes.get500()


		self.filePath = filePath

		self.debug.printMessage("Good message. Generating 200 OK response...")
		# html = "<html><body><h1>200 OK</h1></body></html>\r\n\r\n"

		statusLine = "HTTP/1.0 200 OK\r\n"

		t = time.time()
		current_time = self.errorCodes.get_time(t)
		headers = "Date: %s\r\n" % current_time

		headers += "Server: freeServer/1.0 totallyAwesome\r\n"

		fileExt = filePath.split(".")[-1]
		contentType = self.webServerConfig.getMediaType(fileExt)
		headers += "Content-Type: %s\r\n" % contentType

		size = os.stat(filePath).st_size
		headers += "Content-Length: %d\r\n" % size

		mod_time = os.stat(filePath).st_mtime
		gmtModTime = self.errorCodes.get_time(mod_time)
		headers += "Last-Modified: %s\r\n" % gmtModTime

		headers += "\r\n"
		response = statusLine + headers

		self.debug.printMessage("Response: " + response)
		return response

	def getFilePath(self):
		return self.filePath