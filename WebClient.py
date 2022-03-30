#
# Designed and written by Damian Coventry
# Copyright (c) 2022, all rights reserved
#
# Massey University
# 159.352 Advanced Web Development
# Assignment 1
# 2022 Semester 1
#

from typing import Final
from Http import Http
from HttpRequest import HttpRequest
from Utility import logMessage


class WebClient:
    _READ_SIZE: Final = 10240

    def __init__(self, socket, address):
        self._socket = socket
        self._address = address
        self._request = None

    def disconnect(self):
        self._socket.close()

    def getAddress(self):
        return self._address

    def getRequest(self):
        return self._request

    def readRequest(self):
        rawBytes = self._socket.recv(self._READ_SIZE)
        logMessage(f'Received {len(rawBytes)} bytes')
        self._request = HttpRequest(rawBytes)

        if self._request.hasContentLength():
            if self._request.hasEmptyBody():
                rawBytes = self._socket.recv(self._READ_SIZE)
                self._request.setBody(rawBytes)
                logMessage(f'Has content, executed a second receive, {len(self._request.getBody())} bytes')
            else:
                logMessage(f'Has content, already received it, {len(self._request.getBody())} bytes')

        if not self._request.isEmpty():
            logMessage(self._request.getMethod() + ' ' + self._request.getPath())
            form = self._request.getFormVariables()
            if len(form) > 0:
                logMessage(form)

    def writeResponse(self, headers, body):
        self._socket.sendall((headers + Http.LINE_ENDING).encode())

        if body is not None and len(body) > 0:
            self._socket.sendall(body)
