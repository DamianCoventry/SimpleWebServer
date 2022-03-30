#
# Designed and written by Damian Coventry
# Copyright (c) 2022, all rights reserved
#
# Massey University
# 159.352 Advanced Web Development
# Assignment 1
# 2022 Semester 1
#

from socket import *
from typing import Final
from Utility import *
from WebClient import WebClient
from WebWorker import WebWorker


class WebServer:
    _DEFAULT_PORT: Final = 8080
    _PASSWORD_FILE: Final = 'resources/definitelyNotAPasswordFile.txt'

    def __init__(self, port):
        self._loadPassword()
        self._socket = socket(AF_INET, SOCK_STREAM)
        self._socket.bind(('', self._DEFAULT_PORT if port is None else int(port)))

    def getPassword(self):
        return self._password

    def start(self):
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
        self._password = loadFileContents(self._PASSWORD_FILE).decode('UTF-8').strip()
