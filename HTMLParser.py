from Debug import Debug

class HTMLParser:
    """ HTML Parser """
    def __init__(self,debug):
        self.debug = Debug(debug)


    def parse(self, request):
        """ Parse the message/request """
        if request == "":
            return False

        httpRequest = request.split("\r\n")

        self.debug.printMessage("Request: \n\"" + request + "\"")
        self.debug.printMessage("After splitting: ")
        self.debug.printMessage(httpRequest)

        for currentLine in httpRequest:
            pass

        #parsing Request line
        requestLine = httpRequest[0].split()
        self.method = requestLine[0]
        self.uri = requestLine[1]
        self.version = requestLine[2]

        #parsing Header lines
        self.headerDictionary = {}
        currentLine = 1
        currentString = httpRequest[currentLine]

        while currentString != "":
        	header = currentString.split()
        	self.headerDictionary[header[0]] = header[1]

        	currentLine += 1
        	currentString = httpRequest[currentLine]

        return True

    def getMethod(self):
        return self.method
    def getUri(self):
        return self.uri
    def getHost(self):
        if self.headerDictionary.has_key("Host:"):
            return self.headerDictionary["Host:"].split(":")[0]
        else:
            self.debug.printMessage("[Host:] was not found in GET request")
            return ""

    def printAll(self):
    	self.printItem("Method", self.method)
    	self.printItem("URI", self.uri)
    	self.printItem("Version", self.version)

    	for key, value in self.headerDictionary.iteritems():
    		self.printItem("Header Field Name", key)
    		self.printItem("\tHeader Value", value)
        return ""
    def printItem(self, title, message):
    	print title + ": " + "\"" + message + "\""