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
from pybars import Compiler
from Utility import loadFileContents


class JsFileBuilder:
    """
    This class is an implementation of the Builder Design Pattern
    https://en.wikipedia.org/wiki/Builder_pattern

    This class produces a JavaScript page from a text template. The template requires one template arguments. The
    text template engine is pybars3, which is the Python version of Handlebars.js
    https://github.com/wbond/pybars3
    """

    COMMON_STOCKS_TEMPLATE: Final = 'sitePages/commonStocks.js'
    COMMON_STOCKS_URI: Final = f'/{COMMON_STOCKS_TEMPLATE}'

    def __init__(self):
        """Initialises the text template this class uses"""
        self._pybars = Compiler()
        self._commonStocksTemplate = self._pybars.compile(loadFileContents(self.COMMON_STOCKS_TEMPLATE).decode('UTF-8'))

    def makeCommonStocksFile(self, stockSymbols):
        """Produces a JavaScript file representing the currently available stock symbols"""
        return self._commonStocksTemplate({'stockSymbols': stockSymbols}).encode()
