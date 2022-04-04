"""
Designed and written by Damian Coventry
Copyright (c) 2022, all rights reserved

Massey University
159.352 Advanced Web Development
Assignment 1
2022 Semester 1

Using the https://peps.python.org/pep-0258/ convention
"""

from socket import *
from typing import Final
from Utility import *
from WebClient import WebClient
from WebWorker import WebWorker


class WebServer:
    """
    This class implements the core loop of the server. It's a deliberately infinite loop
    for this assignment.

    For production, the core loop would use select() and include some other wait object
    that, when signalled, informs the core loop to end.
    """

    _DEFAULT_PORT: Final = 8080
    _PASSWORD_FILE: Final = 'resources/definitelyNotAPasswordFile.txt'

    def __init__(self, port):
        """Retrieve the password from disk, and set up a socket for listening with"""
        self._loadPassword()
        self._socket = socket(AF_INET, SOCK_STREAM)  # only TCP over IPv4 supported
        # Bind to a default port if one was not supplied
        self._socket.bind(('', self._DEFAULT_PORT if port is None else int(port)))

    def getPassword(self):
        """Provides access to the password so that Authorization headers can be checked later"""
        return self._password

    def listen(self):
        """
        Implements the core, infinite loop of the server. Each received connection is processed
        within its own thread.

        After accepting a new connection, if the server didn't load a password from disk, then
        it immediately sends an HTTP 503 response code to the client. For this use case, any
        received data from the client are ignored.

        If the accepted connection sends no data, then the server responds with an HTTP 400
        response code. If the accepted connection sends data that cannot be recognised as HTTP,
        then the server responds with an HTTP 400 response code.

        Any valid HTTP request that does not provide an Authorization header, results in an HTTP
        401 response code being sent to the client. Any valid HTTP request that is neither GET
        nor POST results in an HTTP 405 response code being sent to the client.
        
        If the server catches any thrown exception during the processing of an accepted connection,
        then it sends an HTTP 500 response code to the client.

        For all other use cases, the server sends an HTTP 200 response code to the client.
        """

        self._socket.listen(1)
        logMessage('WebServer is ready to receive HTTP requests.')

        while True:
            try:
                sock, address = self._socket.accept()

                worker = WebWorker(self, WebClient(sock, address))
                worker.start()

            except Exception as ex:
                logMessage(f'Exception caught: {ex}')

    def _loadPassword(self):
        """Reads a password from a file on disk. None can be returned."""
        self._password = loadFileContents(self._PASSWORD_FILE).decode('UTF-8').strip()
