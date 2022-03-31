"""
Designed and written by Damian Coventry
Copyright (c) 2022, all rights reserved

Massey University
159.352 Advanced Web Development
Assignment 1
2022 Semester 1

Using the https://peps.python.org/pep-0258/ convention
"""

from Http import Http


class HttpResponseBuilder:
    """
    This class is an implementation of the Builder Design Pattern
    https://en.wikipedia.org/wiki/Builder_pattern

    This class produces HTTP compliant headers
    """

    def __init__(self, httpVersion):
        """Initialises private state used for developer convenience"""
        self._httpVersion = httpVersion
        self._separator = Http.HEADER_SEP

    def makeOK(self):
        """Produces an HTTP compliant 200 OK response header"""
        return self._makeResponse(Http.OK)

    def makeBadRequest(self):
        """Produces an HTTP compliant 400 Bad Request response header"""
        return self._makeResponse(Http.BAD_REQUEST)

    def makeUnauthorized(self):
        """Produces an HTTP compliant 401 Unauthorized response header"""
        return self._makeResponse(Http.UNAUTHORIZED)

    def makeNotFound(self):
        """Produces an HTTP compliant 404 Not Found header"""
        return self._makeResponse(Http.NOT_FOUND)

    def makeMethodNotAllowed(self):
        """Produces an HTTP compliant 405 Method Not Allowed response header"""
        return self._makeResponse(Http.METHOD_NOT_ALLOWED)

    def makeInternalServerError(self):
        """Produces an HTTP compliant 500 Internal Server Error response header"""
        return self._makeResponse(Http.INTERNAL_SERVER_ERROR)

    def makeServiceUnavailable(self):
        """Produces an HTTP compliant 503 Service Unavailable response header"""
        return self._makeResponse(Http.SERVICE_UNAVAILABLE)

    def makeContentType(self, contentType):
        """Produces an HTTP compliant Content-Type header"""
        return self._makeHeader(Http.CONTENT_TYPE, contentType)

    def makeContentLength(self, contentLength):
        """Produces an HTTP compliant Content-Length header"""
        return self._makeHeader(Http.CONTENT_LENGTH, str(contentLength))

    def makeWwwAuthenticate(self, authType, realm):
        """Produces an HTTP compliant WWW-Authenticate header"""
        return self._makeHeader(Http.WWW_AUTHENTICATE, f'{authType} realm=\'{realm}\'')

    def _makeResponse(self, responseCode):
        """Produces an HTTP compliant response header"""
        return f'{self._httpVersion} {responseCode}{Http.LINE_ENDING}'

    def _makeHeader(self, key, value):
        """Produces an HTTP compliant header"""
        return f'{key}{self._separator} {value}{Http.LINE_ENDING}'
