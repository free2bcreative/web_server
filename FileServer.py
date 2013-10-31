from Debug import Debug
from ErrorResponseCodes import ErrorResponseCodes

class FileServer:
    """ FileServer """
    def __init__(self, webServerConfig,debug):
        self.debug = Debug(debug)
        self.webServerConfig = webServerConfig
        self.errorCodes = ErrorResponseCodes()

    def getResponse(self, htmlParser):
    	# check if valid GET request
    	if not htmlParser.getMethod() == "GET":
    		return self.errorCodes.get400()