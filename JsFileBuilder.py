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
from pybars import Compiler
from Utility import loadFileContents


# https://en.wikipedia.org/wiki/Builder_pattern
class JsFileBuilder:
    COMMON_STOCKS_TEMPLATE: Final = 'sitePages/commonStocks.js'
    COMMON_STOCKS_URI: Final = f'/{COMMON_STOCKS_TEMPLATE}'

    def __init__(self):
        self._pybars = Compiler()
        self._commonStocksTemplate = self._pybars.compile(loadFileContents(self.COMMON_STOCKS_TEMPLATE).decode('UTF-8'))

    def makeCommonStocksFile(self, stockSymbols):
        return self._commonStocksTemplate({'stockSymbols': stockSymbols}).encode()
