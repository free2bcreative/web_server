import time
import os

class ErrorResponseCodes():
	"""docstring for ErrorResponseCodes"""
	def getFullResponse(self, responseCode):
		html = "<html><body><h1>%s</h1></body></html>" % responseCode
		statusLine = "HTTP/1.0 %s\r\n" % responseCode

		return statusLine + self.getHeaders(len(html)) + html

	def get400(self):
		""" Bad Request: if the web server parses 
		the request and the method or URI is empty, 
		or if the request contains a host that this 
		server doesn't handle """
		
		return self.getFullResponse("400 Bad Request")

	def get403(self):
		""" Forbidden: if the web server does not 
		have permission to open the requested file """

		return self.getFullResponse("403 Forbidden")

	def get404(self):
		""" Not Found: if the web server cannot 
		find the requested file """

		return self.getFullResponse("404 Not Found")

	def get500(self):
		""" Internal Server Error: if the web server 
		encounters any other error when trying to open 
		a file """

		return self.getFullResponse("500 Internal Server Error")

	def get501(self):
		""" Not Implemented: if the web server does 
		not implement the requested method """

		return self.getFullResponse("501 Not Implemented")

	def get_time(self, t):
		gmt = time.gmtime(t)
		format = '%a, %d %b %Y %H:%M:%S GMT'
		time_string = time.strftime(format,gmt)
		return time_string

	def getHeaders(self, contentLength):
		t = time.time()
		current_time = self.get_time(t)
		headers = current_time + "\r\n"
		headers += "Content-Type: text/html\r\n"
		headers += "Content-Length: %d\r\n" % contentLength
		headers += "\r\n"
		return headers