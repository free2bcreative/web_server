from Debug import Debug

class FileServer:
    """ FileServer """
    def __init__(self,parser, webServerConfig,debug):
        self.debug = Debug(debug)
        self.parser = parser
        self.webServerConfig = webServerConfig


    def parse(self, request):
        """ Parse the message/request """
