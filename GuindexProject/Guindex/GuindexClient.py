import socket
import logging

logger = logging.getLogger(__name__)


class GuindexClient(object):

    def __init__(self, serverName, serverIp, serverPort):

        self.serverName  = serverName
        self.serverIp    = serverIp
        self.serverPort  = serverPort
        self._connection = self._createConnection()

        logger.debug("Created %s client %s", self.serverName, self)

    def __del__(self):

        logger.debug("Destroying %s client %s", self.serverName, self)
        self._connection.close()

    def _createConnection(self):

        fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            logger.info("Creating TCP connection to %s server", self.serverName)
            fd.connect((self.serverIp, self.serverPort))
            logger.info("Successfully connected to %s server", self.serverName)
        except socket.error:
            logger.error("Failed to connect to %s server", self.serverName)
            fd.close()
            raise Exception("Failed to connect to %s server" % self.serverName)

        return fd

    def sendMessage(self, message, prependTwoByteHeader = True):
        """
            Sends string 'message' to server
            (prepending two byte length header by default)
        """

        logger.debug("Sending message to %s server - %s", self.serverName, ":".join("{:02x}".format(ord(c)) for c in message))

        if prependTwoByteHeader:

            logger.debug("Prepending two byte length header to message")

            message_length = len(message)

            logger.debug("Message length = %d", message_length)

            message_length_first_byte = (message_length >> 8) & 0xFF
            message_length_second_byte = message_length & 0xFF
            message = chr(message_length_first_byte) + chr(message_length_second_byte) + message

            logger.debug("Updated message - %s", ":".join("{:02x}".format(ord(c)) for c in message))

        try:
            self._connection.send(message)
        except:
            logger.error("Failed to send message to %s server", self.serverName)
            raise Exception("Failed to send message to %s server" % self.serverName)

            logger.info("Successfully sent message to %s server", self.serverName)
