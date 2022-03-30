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


class RoutingTable:
    _ARBITRARY_ROUTE: Final = '*'

    def __init__(self):
        self._routingTable = {}

    def add(self, route, handler):
        if route not in self._routingTable:
            self._routingTable[route] = handler

    def addArbitrary(self, handler):
        if self._ARBITRARY_ROUTE not in self._routingTable:
            self._routingTable[self._ARBITRARY_ROUTE] = handler

    def dispatch(self, request):
        if request.getPath() in self._routingTable:
            return self._routingTable[request.getPath()](request)

        if self._ARBITRARY_ROUTE in self._routingTable:
            return self._routingTable[self._ARBITRARY_ROUTE](request)

        return None, None  # caller can respond with a 404 Not Found
