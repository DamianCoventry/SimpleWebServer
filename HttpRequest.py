"""
Designed and written by Damian Coventry
Copyright (c) 2022, all rights reserved

Massey University
159.352 Advanced Web Development
Assignment 1
2022 Semester 1

Using the https://peps.python.org/pep-0258/ convention
"""

import base64
from Http import Http
from Utility import isNoneOrEmpty


class HttpRequest:
    """
    This class represents the state of an HTTP request. Other parts of the code can easily retrieve
    received headers and body data by using the public accessor methods.
    """

    def __init__(self, data):
        """Provide well known names for frequently accessed data"""
        self._requestLine = []
        self._headers = {}
        self._body = b''
        self._parseHeaders(data)

    def isEmpty(self):
        """Returns true if no bytes were received for this request, false otherwise"""
        return len(self._requestLine) == 0

    def getMethod(self):
        """Returns either the string 'GET' or 'POST', representing the requested action. Throws an exception
        for all other request types."""
        if len(self._requestLine) == 0:
            return ''

        if self._requestLine[0] == Http.GET or self._requestLine[0] == Http.POST:
            return self._requestLine[0]

        raise Exception(f'Unsupported HTTP method \'{self._requestLine[0]}\'')

    def getPath(self):
        """Returns the path of the object being requested"""
        return self._requestLine[1] if len(self._requestLine) > 0 else ''

    def hasAuthorization(self):
        """Returns true if an Authorization header was received for this request, false otherwise"""
        return Http.AUTHORIZATION in self._headers

    def hasContentLength(self):
        """Returns true if a Content-Length header was received for this request, false otherwise"""
        return Http.CONTENT_LENGTH in self._headers

    def getContentLength(self):
        """Returns the value of the Content-Length header as an integer. Returns None if the
        header is absent."""
        return int(self._headers[Http.CONTENT_LENGTH]) if self.hasContentLength() else None

    def hasEmptyBody(self):
        """Returns true if no bytes were received for this request, false otherwise"""
        return isNoneOrEmpty(self._body)

    def getBody(self):
        """Returns the bytes received that represents the body of the request. Can be None."""
        return self._body

    def setBody(self, data):
        """Stores the passed in data as the bytes of the body for this request"""
        self._body = data

    def getFormVariables(self):
        """Returns a dictionary that represents the form variables bundled within this request"""
        if self.hasEmptyBody():
            return {}

        # Expecting the body bytes to be formatted like this:
        #       symbol=QTRX&quantity=100&price=0.85

        nameValueAssignments = self._body.decode('UTF-8').split(Http.FORM_VAR_SEP)  # split on '&' first
        if isNoneOrEmpty(nameValueAssignments):
            return {}

        form = {}
        for nameValueAssignment in nameValueAssignments:
            nameValue = nameValueAssignment.split(Http.NAME_VALUE_SEP)  # split on '=' next

            # it's ok if there's no value, but there must be a key
            if not isNoneOrEmpty(nameValue):
                form[nameValue[0]] = nameValue[1] if not isNoneOrEmpty(nameValue[1]) else ''

        return form

    def getAuthorization(self):
        """Unpacks the Authorization header and returns its parts. Returns an empty array
        if an Authorization header is absent."""
        if not self.hasAuthorization():
            return []

        authType = self._headers[Http.AUTHORIZATION].split()
        if len(authType) != 2:  # handle a malformed case
            return []

        credentials = base64.b64decode(authType[1]).decode('UTF-8').split(Http.HEADER_SEP)
        if len(credentials) != 2:  # handle a malformed case
            return []

        return [authType[0], credentials[0], credentials[1]]

    def _parseHeaders(self, rawBytes):
        """Clears internal state, then rebuilds it from the passed in bytes. If the bytes are
        not in a recognisable format then the internal state remains cleared."""
        self._requestLine = []
        self._headers = {}
        self._body = b''

        if isNoneOrEmpty(rawBytes):  # handle the None argument case
            return

        lines = rawBytes.decode('UTF-8').splitlines(False)  # we're expecting lines of utf8 text
        if isNoneOrEmpty(lines):
            return

        # the approach is to split the data by lines, consume the first line, then iterate
        # over the remaining lines.
        # the first line is assumed to be an HTTP request line, and therefore is formatted
        # differently to the other lines.

        self._requestLine = lines[0].split()  # Expecting ['GET', '/portfolio', 'HTTP/1.1']

        # the remaining lines are expected to be key value pairs separated by a ':' character.
        # when we encounter an empty line while iterating, we assume this is the end of the
        # HTTP headers. all remaining lines are stored as body data.
        # we discard any lines not separated by a ':' character, and we discard the empty line.

        startBody = False
        for i in range(1, len(lines)):  # start from index 1 (i.e. skip over the request line)
            if startBody:  # found an empty line yet?
                self._body += lines[i].encode()

            elif len(lines[i]) > 0:  # is it empty?
                keyValue = lines[i].split(Http.HEADER_SEP)

                if not isNoneOrEmpty(keyValue):
                    # it's ok if there's no value, but there must be a key
                    if len(keyValue) > 1:
                        # the Http.HEADER_SEP.join() code after this comment is there to restore any
                        # additionally stripped ':' characters, such as between the '127.0.0.1:8080'
                        # IP address in the 'Host:' header
                        self._headers[keyValue[0].strip()] = Http.HEADER_SEP.join(keyValue[1:]).strip()

                    else:
                        self._headers[keyValue[0].strip()] = ''

            else:
                startBody = True  # the remaining lines are appended as body data
