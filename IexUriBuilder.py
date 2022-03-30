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


# https://en.wikipedia.org/wiki/Builder_pattern
class IexUriBuilder:
    _SYMBOLS: Final = u'https://cloud.iexapis.com/stable/ref-data/symbols'
    _QUOTE: Final = u'https://cloud.iexapis.com/stable/stock/{{stockSymbol}}/quote'
    _STATISTICS: Final = u'https://cloud.iexapis.com/stable/stock/{{stockSymbol}}/stats'
    _CHART: Final = u'https://cloud.iexapis.com/stable/stock/{{stockSymbol}}/chart/5y?chartCloseOnly=true'

    def __init__(self):
        self._pybars = Compiler()
        self._quoteUri = self._pybars.compile(self._QUOTE)
        self._statisticsUri = self._pybars.compile(self._STATISTICS)
        self._chartUri = self._pybars.compile(self._CHART)

    def makeSymbolsUri(self):
        return self._SYMBOLS

    def makeQuoteUri(self, stockSymbol):
        return self._quoteUri({'stockSymbol': stockSymbol})

    def makeStatisticsUri(self, stockSymbol):
        return self._statisticsUri({'stockSymbol': stockSymbol})

    def makeChartUri(self, stockSymbol):
        return self._chartUri({'stockSymbol': stockSymbol})
