"""
Designed and written by Damian Coventry
Copyright (c) 2022, all rights reserved

Massey University
159.352 Advanced Web Development
Assignment 1
2022 Semester 1

Using the https://peps.python.org/pep-0258/ convention
"""

import json
import requests
from typing import Final
from IexUriBuilder import IexUriBuilder
from Utility import *


class IexApi:
    """
    This class is an implementation of the Facade Design Pattern
    https://en.wikipedia.org/wiki/Facade_pattern

    This class hides the implementation details required for communicating with the IEX web service. This
    includes the TCP/IP communication, and how a stock symbol is used to identify a remote resource.
    """

    _PLEASE_UPGRADE_MESSAGE: Final = 'You have used all available credits for the month. Please upgrade ' +\
                                     'or purchase additional packages to access more data.'

    def __init__(self, apiKey):
        """Stores the IEX API key for later use, and initialises the URI builder"""
        self._apiKey = apiKey
        self._uriBuilder = IexUriBuilder()

    def fetchCommonStockSymbols(self):
        """Retrieves all stocks from the IEX system, then filters locally for 'Common Stocks'"""
        uri = self._uriBuilder.makeSymbolsUri()
        allSymbols = self._fetchJson(uri, 'exampleData/stock_symbols.js')
        return [stock for stock in allSymbols if 'type' in stock and stock['type'].lower() == 'cs']

    def fetchQuote(self, stockSymbol):
        """Retrieves a quote for a stock symbol from the IEX system"""
        uri = self._uriBuilder.makeQuoteUri(stockSymbol)
        return self._fetchJson(uri, 'exampleData/stock_quote.js')

    def fetchStatistics(self, stockSymbol):
        """Retrieves statistics for a stock symbol from the IEX system"""
        uri = self._uriBuilder.makeStatisticsUri(stockSymbol)
        return self._fetchJson(uri, 'exampleData/stock_statistics.js')

    def fetchChartDataPoints(self, stockSymbol):
        """Retrieves chart data points for a stock symbol from the IEX system"""
        uri = self._uriBuilder.makeChartDataPointsUri(stockSymbol)
        return self._fetchJson(uri, 'exampleData/stock_data_points.js')

    def _fetchJson(self, uri, alternative):
        """Sends an HTTP GET request to the IEX system, assumes the return value is utf8 text formatted
        as JSON, then proceeds to unpack it into a JSON object"""
        logMessage(f'IEX: {uri}')

        token = '&token=' if uri.rfind('?') >= 0 else '?token='  # handle the case of an already present query string
        jsonText = requests.get(uri + token + self._apiKey).text

        # watch out -- the free plan from IEX has limits. if we get this string then just bundle our old,
        # stale data, and send it back to the browser.
        if jsonText == self._PLEASE_UPGRADE_MESSAGE:
            logMessage(f'Using cached data from \'{alternative}\'')
            return json.loads(loadFileContents(alternative))

        if jsonText.lower() == 'unknown symbol':  # handle an error case
            return None

        return json.loads(jsonText)
