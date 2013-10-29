from Debug import Debug

class HTMLParser:
    """ HTML Parser """
    def __init__(self,request,debug):
        self.debug = Debug(debug)
        self.parse(request)


    def parse(self, request):
        """ Parse the message/request """
        httpRequest = request.split("\r\n")

        self.debug.printMessage("Request: \n\"" + request + "\"")
        self.debug.printMessage("After splitting: ")
        self.debug.printMessage(httpRequest)

        for currentLine in httpRequest:
            pass

        #parsing Request line
        requestLine = httpRequest[0].split()
        self.method = requestLine[0]
        self.url = requestLine[1]
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

        #parsing entity body (if needed)
        currentLine += 1
        if len(httpRequest) - 1 == currentLine:
        	self.entityBody = httpRequest[currentLine]
        else:
        	self.entityBody = None

    def printAll(self):
    	self.printItem("Method", self.method)
    	self.printItem("URL", self.url)
    	self.printItem("Version", self.version)

    	for key, value in self.headerDictionary.iteritems():
    		self.printItem("Header Field Name", key)
    		self.printItem("\tHeader Value", value)

    	if self.entityBody:
    		self.printItem("Entity Body", self.entityBody)

    def printItem(self, title, message):
    	print title + ": " + "\"" + message + "\""