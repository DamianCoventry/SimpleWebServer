"""
Designed and written by Damian Coventry
Copyright (c) 2022, all rights reserved

Massey University
159.352 Advanced Web Development
Assignment 1
2022 Semester 1

Using the https://peps.python.org/pep-0258/ convention
"""

from typing import Final
from Http import Http
from HttpRequest import HttpRequest
from Utility import *


class WebClient:
    """
    This class holds on to the socket that was accepted for the client connection.

    The main functionality provided here is to read/write bytes from/to the socket. The
    read bytes are bundled into an HttpRequest object. This object is easily retrievable
    any time other code needs to know what was received from the client. The HttpRequest
    object provides convenient access to the byte unpacking methods required by HTTP.

    The write functionality provided here ensures that there is always an empty line
    terminating the HTTP headers, and provides a trivial check for body data.
    """

    _READ_SIZE: Final = 10240

    def __init__(self, socket, address):
        """Save the client's socket and IP address for later use. Give the request object a name."""
        self._socket = socket
        self._address = address
        self._request = None
        logMessage(f'Connected to {self._address}')

    def disconnect(self):
        """End the connection with the client"""
        logMessage(f'Disconnected from {self._address}')
        self._socket.close()

    def getAddress(self):
        """Provide a reference to the client's IP address"""
        return self._address

    def getRequest(self):
        """Provide a reference to the HTTP request the client has sent"""
        return self._request

    def readRequest(self):
        """
        Reads bytes from the client's socket, then bundles them into an HttpRequest object for
        subsequent inspection.

        A big gotcha here is that the runtime behaviour differs greatly when executing locally
        against 'localhost', to that of executing remotely within the Heroku system.

        The obvious speed differences aside, the issue is Heroku uses a forwarding proxy. Sometimes
        that proxy forwards all of an HTTP request to the web server within one transmission unit,
        sometimes it doesn't. The result being sometimes one needs to call recv() once, sometimes
        twice.

        To be really robust, this code should be updated to check if all the requested bytes
        were received or not. Currently, this code asks for 10k of data with the underlying
        assumption that this amount of data will never be received in one read. If this many
        bytes were received, then the following code would be blissfully unaware of data past
        the 10k mark.
        """

        rawBytes = self._socket.recv(self._READ_SIZE)
        logMessage(f'Received {len(rawBytes)} bytes')
        self._request = HttpRequest(rawBytes)

        if self._request.hasContentLength():  # does this request have body data?
            # did that first read supply the body data?
            if self._request.hasEmptyBody():
                rawBytes = self._socket.recv(self._request.getContentLength())  # we need to read again
                self._request.setBody(rawBytes)
                logMessage(f'Has content, performed a second receive, {len(self._request.getBody())} bytes')

            else:
                logMessage(f'Has content, already received it, {len(self._request.getBody())} bytes')

        # dump some additional logging information to stdout
        if not self._request.isEmpty():
            logMessage(self._request.getMethod() + ' ' + self._request.getPath())

            form = self._request.getFormVariables()
            if len(form) > 0:
                logMessage(form)

    def writeResponse(self, headers, body):
        """Sends the header data, and optionally the body data, to the client. The header has
        a newline appended before being sent."""
        self._socket.sendall((headers + Http.LINE_ENDING).encode())

        if not isNoneOrEmpty(body):
            self._socket.sendall(body)
