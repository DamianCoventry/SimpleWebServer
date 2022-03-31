"""
Designed and written by Damian Coventry
Copyright (c) 2022, all rights reserved

Massey University
159.352 Advanced Web Development
Assignment 1
2022 Semester 1

Using the https://peps.python.org/pep-0258/ convention
"""

import os
from typing import Final
from pybars import Compiler
from Utility import loadFileContents


class HtmlPageBuilder:
    """
    This class is an implementation of the Builder Design Pattern
    https://en.wikipedia.org/wiki/Builder_pattern

    This class produces complete HTML pages from text templates. Each template requires one or more
    template arguments. The text template engine is pybars3, which is the Python version of Handlebars.js
    https://github.com/wbond/pybars3
    """

    _PORTFOLIO_TEMPLATE: Final = 'sitePages/portfolio.html'
    _RESEARCH_TEMPLATE: Final = 'sitePages/research.html'
    _500_ERROR_TEMPLATE: Final = 'errorPages/500.html'

    def __init__(self):
        """Initialises the text templates this class uses"""
        self._pybars = Compiler()
        self._portfolioTemplate = self._pybars.compile(loadFileContents(self._PORTFOLIO_TEMPLATE).decode('UTF-8'))
        self._researchTemplate = self._pybars.compile(loadFileContents(self._RESEARCH_TEMPLATE).decode('UTF-8'))
        self._500ErrorTemplate = self._pybars.compile(loadFileContents(self._500_ERROR_TEMPLATE).decode('UTF-8'))

    def makePortfolioPage(self, errorMessageHtml, stockRowsHtml):
        """Produces an HTML page representing the current state of the portfolio"""
        return self._portfolioTemplate(
            {
                'errorMessage': errorMessageHtml,
                'stockRows': stockRowsHtml
            }).encode()

    def makeResearchPage(self, errorMessageHtml, companyNameJs, dataPointsJs, statisticsHtml):
        """Produces an HTML page representing research for a stock symbol"""
        return self._researchTemplate(
            {
                'errorMessage': errorMessageHtml,
                'companyName': companyNameJs,
                'dataPoints': dataPointsJs,
                'stockStatistics': statisticsHtml
            }).encode()

    def makeErrorPage(self, httpResponseCode, errorMessageHtml):
        """Produces an HTML page describing an error the web server has suffered"""
        fileName = f'errorPages/{httpResponseCode}.html'
        if os.path.exists(fileName) and httpResponseCode != 500:
            return loadFileContents(fileName)

        return self._500ErrorTemplate({'errorMessage': errorMessageHtml}).encode()
