class Debug:
    """ Debug messages """
    def __init__(self, debug):
        self.debug = debug

    def printMessage(self, message):
        if self.debug:
            print "DEBUG: ",
            print message

    def isDebug(self):
    	return self.debug