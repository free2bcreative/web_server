from Debug import Debug
from ErrorResponseCodes import ErrorResponseCodes

class FileServer:
	""" FileServer """
	def __init__(self, webServerConfig,debug):
		self.debug = Debug(debug)
		self.webServerConfig = webServerConfig
		self.errorCodes = ErrorResponseCodes()
		self.filePath = ""

	def getResponse(self, htmlParser):
		self.filePath = ""

		# check if valid GET request
		self.debug.printMessage("Checking if valid GET request...")
		if not htmlParser.getMethod() == "GET":
			return self.errorCodes.get400()

		# translate URI to filename
		self.debug.printMessage("Translating request to URL...")
		host = htmlParser.getHost()
		uri = htmlParser.getUri()
		filePath = host + uri
		self.debug.printMessage("FilePath: " + filePath)

		# check if good filePath or no permissions given
		self.debug.printMessage("Checking if good filePath or no permissions given")
		try:
			f = open(filePath)
			print "Opened just fine"
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


		self.debug.printMessage("Good message. Generating 200 OK response...")
		html = "<html><body><h1>200 OK</h1></body></html>\r\n\r\n"

		statusLine = "HTTP/1.0 200 OK\r\n"
		t = time.time()
		current_time = self.errorCodes.get_time(t)
		headers = current_time + "\r\n"
		headers += "Content-Type: text/html\r\n"
		headers += "Content-Length: %d\r\n" % html.__len__()
		headers += "\r\n"
		response = headers + html

		self.debug.printMessage("Response: " + response)
		return response