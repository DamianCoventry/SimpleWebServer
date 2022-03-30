#
# Designed and written by Damian Coventry
# Copyright (c) 2022, all rights reserved
#
# Massey University
# 159.352 Advanced Web Development
# Assignment 1
# 2022 Semester 1
#

import base64
from Http import Http


class HttpRequest:
    def __init__(self, data):
        self._requestLine = []
        self._headers = {}
        self._body = b''
        self._parseHeaders(data)

    def isEmpty(self):
        return len(self._requestLine) == 0

    def getMethod(self):
        if self._requestLine[0] == Http.GET or self._requestLine[0] == Http.POST:
            return self._requestLine[0]

        raise Exception(f'Unsupported HTTP method \'{self._requestLine[0]}\'')

    def getPath(self):
        return self._requestLine[1]

    def getHeaders(self):
        return self._headers

    def hasAuthorization(self):
        return Http.AUTHORIZATION in self._headers

    def hasContentLength(self):
        return Http.CONTENT_LENGTH in self._headers

    def hasEmptyBody(self):
        return self._body is None or len(self._body) == 0

    def getBody(self):
        return self._body

    def setBody(self, data):
        self._body = data

    def getFormVariables(self):
        if self.hasEmptyBody():
            return {}

        nameValueAssignments = self._body.decode('UTF-8').split(Http.FORM_VAR_SEP)
        if nameValueAssignments is None or len(nameValueAssignments) == 0:
            return {}

        form = {}
        for nameValueAssignment in nameValueAssignments:
            nameValue = nameValueAssignment.split(Http.NAME_VALUE_SEP)

            if nameValue is not None:
                form[nameValue[0]] = nameValue[1] if nameValue[1] is not None else ''

        return form

    def getAuthorization(self):
        if not self.hasAuthorization():
            return []

        authType = self._headers[Http.AUTHORIZATION].split()
        if len(authType) != 2:
            return []

        credentials = base64.b64decode(authType[1]).decode('UTF-8').split(Http.HEADER_SEP)
        if len(credentials) != 2:
            return []

        return [authType[0], credentials[0], credentials[1]]

    def _parseHeaders(self, rawBytes):
        self._requestLine = []
        self._headers = {}
        self._body = b''

        if rawBytes is None or len(rawBytes) == 0:
            return

        lines = rawBytes.decode('UTF-8').splitlines(False)
        if lines is None or len(lines) == 0:
            return

        self._requestLine = lines[0].split()
        startBody = False
        for i in range(1, len(lines)):  # start from index 1 (i.e. skip over the request line)
            if startBody:
                self._body += lines[i].encode()

            elif len(lines[i]) > 0:
                keyValue = lines[i].split(Http.HEADER_SEP)

                if keyValue is not None and len(keyValue) > 0:
                    if len(keyValue) > 1:
                        self._headers[keyValue[0].strip()] = Http.HEADER_SEP.join(keyValue[1:]).strip()

                    else:
                        self._headers[keyValue[0].strip()] = ''

            else:
                startBody = True
