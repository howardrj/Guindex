import socket


class GuindexClient():

    def __init__(self, logger, serverName, serverIp, serverPort):

        self.logger      = logger
        self.serverName  = serverName
        self.serverIp    = serverIp
        self.serverPort  = serverPort
        self._connection = self._createConnection()

        self.logger.debug("Created %s client %s", self.serverName, self)

    def __del__(self):

        self.logger.debug("Destroying %s client %s", self.serverName, self)
        self._connection.close()

    def _createConnection(self):

        fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.logger.info("Creating TCP connection to %s server", self.serverName)
            fd.connect((self.serverIp, self.serverPort))
            self.logger.info("Successfully connected to %s server", self.serverName)
        except socket.error:
            self.logger.error("Failed to connect to %s server", self.serverName)
            fd.close()
            raise Exception("Failed to connect to %s server" % self.serverName)

        return fd

    def sendMessage(self, message, prependTwoByteHeader = True):
        """
            Sends string 'message' to server
            (prepending two byte length header by default)
        """

        self.logger.debug("Sending message to %s server - %s", self.serverName, ":".join("{:02x}".format(ord(c)) for c in message))

        if prependTwoByteHeader:

            self.logger.debug("Prepending two byte length header to message")

            message_length = len(message)

            self.logger.debug("Message length = %d", message_length)

            message_length_first_byte = (message_length >> 8) & 0xFF
            message_length_second_byte = message_length & 0xFF
            message = chr(message_length_first_byte) + chr(message_length_second_byte) + message

            self.logger.debug("Updated message - %s", ":".join("{:02x}".format(ord(c)) for c in message))

        try:
            self._connection.send(message)
        except:
            self.logger.error("Failed to send message to %s server", self.serverName)
            raise Exception("Failed to send message to %s server" % self.serverName)
