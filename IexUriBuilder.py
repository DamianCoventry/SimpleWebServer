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


class IexUriBuilder:
    """
    This class is an implementation of the Builder Design Pattern
    https://en.wikipedia.org/wiki/Builder_pattern

    This class produces complete HTML pages from text templates. Each template requires one or more
    template arguments. The text template engine is pybars3, which is the Python version of Handlebars.js
    https://github.com/wbond/pybars3
    """

    _SYMBOLS_TEMPLATE: Final = u'https://cloud.iexapis.com/stable/ref-data/symbols'
    _QUOTE_TEMPLATE: Final = u'https://cloud.iexapis.com/stable/stock/{{stockSymbol}}/quote'
    _CHART_DATA_POINTS_TEMPLATE: Final =\
        u'https://cloud.iexapis.com/stable/stock/{{stockSymbol}}/chart/5y?chartCloseOnly=true'
    _STATISTICS_TEMPLATE: Final = u'https://cloud.iexapis.com/stable/stock/{{stockSymbol}}/stats'

    def __init__(self):
        """Initialises the text templates this class uses"""
        self._pybars = Compiler()
        self._quoteUriTemplate = self._pybars.compile(self._QUOTE_TEMPLATE)
        self._chartDataPointsUriTemplate = self._pybars.compile(self._CHART_DATA_POINTS_TEMPLATE)
        self._statisticsUriTemplate = self._pybars.compile(self._STATISTICS_TEMPLATE)

    def makeSymbolsUri(self):
        """Produces a URI for retrieving the available stock symbols"""
        return self._SYMBOLS_TEMPLATE

    def makeQuoteUri(self, stockSymbol):
        """Produces a URI for retrieving a quote for a stock symbol"""
        return self._quoteUriTemplate({'stockSymbol': stockSymbol})

    def makeChartDataPointsUri(self, stockSymbol):
        """Produces a URI for retrieving data points of a stock symbol for a graph"""
        return self._chartDataPointsUriTemplate({'stockSymbol': stockSymbol})

    def makeStatisticsUri(self, stockSymbol):
        """Produces a URI for retrieving statistics for a stock symbol"""
        return self._statisticsUriTemplate({'stockSymbol': stockSymbol})
