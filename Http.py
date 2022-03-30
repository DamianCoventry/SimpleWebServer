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


class Http:
    VERSION: Final = 'HTTP/1.1'

    GET: Final = 'GET'
    POST: Final = 'POST'

    OK: Final = '200 OK'
    BAD_REQUEST: Final = '400 Bad Request'
    UNAUTHORIZED: Final = '401 Unauthorized'
    NOT_FOUND: Final = '404 Not Found'
    METHOD_NOT_ALLOWED: Final = '405 Method Not Allowed'
    INTERNAL_SERVER_ERROR: Final = '500 Internal Server Error'
    SERVICE_UNAVAILABLE: Final = '503 Service Unavailable'

    CONTENT_TYPE: Final = 'Content-Type'
    CONTENT_LENGTH: Final = 'Content-Length'
    AUTHORIZATION: Final = 'Authorization'
    WWW_AUTHENTICATE: Final = 'WWW-Authenticate: Basic realm=\'Portfolio\''

    BASIC_AUTH: Final = 'Basic'
    LINE_ENDING: Final = '\r\n'
    HEADER_SEP: Final = ':'
    FORM_VAR_SEP: Final = '&'
    NAME_VALUE_SEP: Final = '='
