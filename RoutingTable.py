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


class RoutingTable:
    """
    Stores a map of routes to callback functions. The routes in this case are the 'object' or 'path'
    portion of a URI.

    For example, the URI https://web-dev-assgn1-159352.herokuapp.com/portfolio can be serviced by storing
    the route '/portfolio' within this class, and bundling with it a callback that knows about processing
    the portfolio.

    This class also supports a simple 'arbitrary' callback that is a catch-all system for any route the
    user might type into the address bar of their browser. Typically, one would map this to a 'does
    this file exist' and 'should you be able to access it' style callback. Either a 404 Not Found could
    be returned, or the contents of the file.
    """
    _ARBITRARY_ROUTE: Final = '*'

    def __init__(self):
        """Give the dictionary a name"""
        self._routingTable = {}

    def add(self, route, handler):
        """Inserts the route + handler into the table"""
        if route not in self._routingTable:  # don't add duplicates
            self._routingTable[route] = handler

    def addArbitrary(self, handler):
        """Inserts the handler into the table"""
        if self._ARBITRARY_ROUTE not in self._routingTable:  # don't add duplicates
            self._routingTable[self._ARBITRARY_ROUTE] = handler

    def dispatch(self, request):
        """Calls the callback associated with the path within the request. The request object is
        passed to the callback so that it can be processed."""
        if request.getPath() in self._routingTable:  # execute it if we've heard of it
            return self._routingTable[request.getPath()](request)

        if self._ARBITRARY_ROUTE in self._routingTable:  # try the catch-all callback
            return self._routingTable[self._ARBITRARY_ROUTE](request)

        return None, None  # caller can respond with a 404 Not Found
