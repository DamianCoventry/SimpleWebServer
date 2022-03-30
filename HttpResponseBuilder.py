#
# Designed and written by Damian Coventry
# Copyright (c) 2022, all rights reserved
#
# Massey University
# 159.352 Advanced Web Development
# Assignment 1
# 2022 Semester 1
#

from Http import Http


# https://en.wikipedia.org/wiki/Builder_pattern
class HttpResponseBuilder:
    def __init__(self, httpVersion, separator):
        self._httpVersion = httpVersion + ' '
        self._separator = separator + ' '

    def makeOK(self):
        return self._makeResponse(Http.OK)

    def makeBadRequest(self):
        return self._makeResponse(Http.BAD_REQUEST)

    def makeUnauthorized(self):
        return self._makeResponse(Http.UNAUTHORIZED)

    def makeNotFound(self):
        return self._makeResponse(Http.NOT_FOUND)

    def makeMethodNotAllowed(self):
        return self._makeResponse(Http.METHOD_NOT_ALLOWED)

    def makeInternalServerError(self):
        return self._makeResponse(Http.INTERNAL_SERVER_ERROR)

    def makeServiceUnavailable(self):
        return self._makeResponse(Http.SERVICE_UNAVAILABLE)

    def makeContentType(self, contentType):
        return self._makeHeader(Http.CONTENT_TYPE, contentType)

    def makeContentLength(self, contentLength):
        return self._makeHeader(Http.CONTENT_LENGTH, str(contentLength))

    def makeWwwAuthenticate(self, authType, realm):
        return self._makeHeader(Http.WWW_AUTHENTICATE, f'{authType} realm=\'{realm}\'')

    def _makeResponse(self, responseCode):
        return self._httpVersion + responseCode + Http.LINE_ENDING

    def _makeHeader(self, key, value):
        return key + self._separator + value + Http.LINE_ENDING
