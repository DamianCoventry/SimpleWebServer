#
# Designed and written by Damian Coventry
# Copyright (c) 2022, all rights reserved
#
# Massey University
# 159.352 Advanced Web Development
# Assignment 1
# 2022 Semester 1
#

import os
from typing import Final
from pybars import Compiler
from Utility import loadFileContents


# https://en.wikipedia.org/wiki/Builder_pattern
class HtmlPageBuilder:
    _PORTFOLIO_PAGE: Final = 'sitePages/portfolio.html'
    _RESEARCH_PAGE: Final = 'sitePages/research.html'
    _500_ERROR_PAGE: Final = 'errorPages/500.html'

    def __init__(self):
        self._pybars = Compiler()
        self._portfolioPage = self._pybars.compile(loadFileContents(self._PORTFOLIO_PAGE).decode('UTF-8'))
        self._researchPage = self._pybars.compile(loadFileContents(self._RESEARCH_PAGE).decode('UTF-8'))
        self._500ErrorPage = self._pybars.compile(loadFileContents(self._500_ERROR_PAGE).decode('UTF-8'))

    def makePortfolioPage(self, errorMessage, stockRows):
        return self._portfolioPage(
            {
                'errorMessage': errorMessage,
                'stockRows': stockRows
            }).encode()

    def makeResearchPage(self, errorMessage, companyName, dataPoints, stockStatistics):
        return self._researchPage(
            {
                'errorMessage': errorMessage,
                'companyName': companyName,
                'dataPoints': dataPoints,
                'stockStatistics': stockStatistics
            }).encode()

    def makeErrorPage(self, responseCode, errorMessage):
        fileName = f'errorPages/{responseCode}.html'
        if os.path.exists(fileName) and responseCode != 500:
            return loadFileContents(fileName)

        return self._500ErrorPage({'errorMessage': errorMessage}).encode()
