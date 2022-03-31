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
    _SYMBOLS_TEMPLATE: Final = u'https://cloud.iexapis.com/stable/ref-data/symbols'
    _QUOTE_TEMPLATE: Final = u'https://cloud.iexapis.com/stable/stock/{{stockSymbol}}/quote'
    _STATISTICS_TEMPLATE: Final = u'https://cloud.iexapis.com/stable/stock/{{stockSymbol}}/stats'
    _CHART_TEMPLATE: Final = u'https://cloud.iexapis.com/stable/stock/{{stockSymbol}}/chart/5y?chartCloseOnly=true'

    def __init__(self):
        self._pybars = Compiler()
        self._quoteUriTemplate = self._pybars.compile(self._QUOTE_TEMPLATE)
        self._statisticsUriTemplate = self._pybars.compile(self._STATISTICS_TEMPLATE)
        self._chartUriTemplate = self._pybars.compile(self._CHART_TEMPLATE)

    def makeSymbolsUri(self):
        return self._SYMBOLS_TEMPLATE

    def makeQuoteUri(self, stockSymbol):
        return self._quoteUriTemplate({'stockSymbol': stockSymbol})

    def makeStatisticsUri(self, stockSymbol):
        return self._statisticsUriTemplate({'stockSymbol': stockSymbol})

    def makeChartUri(self, stockSymbol):
        return self._chartUriTemplate({'stockSymbol': stockSymbol})
