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
    _PORTFOLIO_TEMPLATE: Final = 'sitePages/portfolio.html'
    _RESEARCH_TEMPLATE: Final = 'sitePages/research.html'
    _500_ERROR_TEMPLATE: Final = 'errorPages/500.html'

    def __init__(self):
        self._pybars = Compiler()
        self._portfolioTemplate = self._pybars.compile(loadFileContents(self._PORTFOLIO_TEMPLATE).decode('UTF-8'))
        self._researchTemplate = self._pybars.compile(loadFileContents(self._RESEARCH_TEMPLATE).decode('UTF-8'))
        self._500ErrorTemplate = self._pybars.compile(loadFileContents(self._500_ERROR_TEMPLATE).decode('UTF-8'))

    def makePortfolioPage(self, errorMessage, stockRows):
        return self._portfolioTemplate(
            {
                'errorMessage': errorMessage,
                'stockRows': stockRows
            }).encode()

    def makeResearchPage(self, errorMessage, companyNameJs, dataPointsJs, statisticsHtml):
        return self._researchTemplate(
            {
                'errorMessage': errorMessage,
                'companyName': companyNameJs,
                'dataPoints': dataPointsJs,
                'stockStatistics': statisticsHtml
            }).encode()

    def makeErrorPage(self, responseCode, errorMessage):
        fileName = f'errorPages/{responseCode}.html'
        if os.path.exists(fileName) and responseCode != 500:
            return loadFileContents(fileName)

        return self._500ErrorTemplate({'errorMessage': errorMessage}).encode()
