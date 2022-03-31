#
# Designed and written by Damian Coventry
# Copyright (c) 2022, all rights reserved
#
# Massey University
# 159.352 Advanced Web Development
# Assignment 1
# 2022 Semester 1
#

import json
import requests
from typing import Final
from IexUriBuilder import IexUriBuilder
from Utility import *


class IexApi:
    _PLEASE_UPGRADE_MESSAGE: Final = 'You have used all available credits for the month. Please upgrade ' +\
                                      'or purchase additional packages to access more data.'

    def __init__(self, apiKey):
        self._apiKey = apiKey
        self._uriBuilder = IexUriBuilder()

    def fetchSymbols(self):
        uri = self._uriBuilder.makeSymbolsUri()
        return self._fetchJson(uri, 'exampleData/stock_symbols.js')

    def fetchQuote(self, stockSymbol):
        uri = self._uriBuilder.makeQuoteUri(stockSymbol)
        return self._fetchJson(uri, 'exampleData/stock_quote.js')

    def fetchStatistics(self, stockSymbol):
        uri = self._uriBuilder.makeStatisticsUri(stockSymbol)
        return self._fetchJson(uri, 'exampleData/stock_statistics.js')

    def fetchChart(self, stockSymbol):
        uri = self._uriBuilder.makeChartUri(stockSymbol)
        return self._fetchJson(uri, 'exampleData/stock_data_points.js')

    def _fetchJson(self, uri, alternative):
        logMessage(f'IEX: {uri}')

        token = '&token=' if uri.rfind('?') >= 0 else '?token='
        jsonText = requests.get(uri + token + self._apiKey).text

        if jsonText == self._PLEASE_UPGRADE_MESSAGE:
            logMessage(f'Using cached data from \'{alternative}\'')
            return json.loads(loadFileContents(alternative))

        if jsonText.lower() == 'unknown symbol':
            return None

        return json.loads(jsonText)
