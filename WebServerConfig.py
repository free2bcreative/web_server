from Debug import Debug

class WebServerConfig:
    """ WebServerConfig """
    def __init__(self,configFilePath,debug):
        self.debug = Debug(debug)
        self.configFilePath = configFilePath
        self.hosts = {}
        self.media = {}
        self.idleTime = 0
        self.parse()


    def parse(self):
        """ Parse the configFilePath """
        # open the file and place in string 
        configString = open(self.configFilePath).read()

        self.debug.printMessage("configString:")
        self.debug.printMessage(configString)

        # split up the different lines
        lines = configString.split("\n")
        self.debug.printMessage("After splitting up:")
        self.debug.printMessage(lines)

        # iterate through lines and place in correct dictionary or int
        for line in lines:
        	words = line.split()

        	if not len(words) == 3:
        		continue

        	self.debug.printMessage("Line:")
        	self.debug.printMessage(line)

        	self.debug.printMessage("After splitting up")
        	self.debug.printMessage(words)

        	if words[0] == "host":
        		self.hosts[words[1]] = words[2]
        	elif words[0] == "media":
        		self.media[words[1]] = words[2]
        	elif words[0] == "parameter":
        		self.idleTime = int(words[2])

	def getPath(self,host):
		""" Looks into dictionary and finds correct path """
		if self.hosts.has_key(host):
			return self.hosts[host]
		else:
			return self.hosts["default"]

	def getMediaType(ext):
		""" Looks into dictionary and finds correct media type """
		if self.media.has_key(ext):
			return self.media[ext]
		else:
			return "text/plain"