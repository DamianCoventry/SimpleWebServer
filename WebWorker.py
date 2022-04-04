"""
Designed and written by Damian Coventry
Copyright (c) 2022, all rights reserved

Massey University
159.352 Advanced Web Development
Assignment 1
2022 Semester 1

Using the https://peps.python.org/pep-0258/ convention
"""

import _thread
from typing import Final
from HtmlPageBuilder import HtmlPageBuilder
from Http import Http
from HttpResponseBuilder import HttpResponseBuilder
from IexApi import IexApi
from Portfolio import Portfolio
from Utility import *
from RoutingTable import RoutingTable
from JsFileBuilder import JsFileBuilder


class WebWorker:
    """
    This class implements the logic for the portfolio website. The start() method is the
    only public method. All other private methods implement the rules of the website.
    """

    _PORTFOLIO_NAME: Final = 'portfolio'
    _PORTFOLIO_URI: Final = f'/{_PORTFOLIO_NAME}'
    _PORTFOLIO_DB: Final = f'portfolioDatabase/{_PORTFOLIO_NAME}.json'

    _RESEARCH_NAME: Final = 'research'
    _RESEARCH_URI: Final = f'/{_RESEARCH_NAME}'

    _NO_ERROR: Final = '&nbsp;'
    _EMPTY_HTML: Final = '&nbsp;'

    _IEX_API_KEY: Final = 'pk_069ce437622a4d38aed7a5cc927be3a8'

    _fileTypeTable: Final = \
        {
            '.ico': 'image/vnd.microsoft.icon',
            '.htm': 'text/html; charset=UTF-8',
            '.html': 'text/html; charset=UTF-8',
            '.css': 'text/; charset=UTF-8',
            '.js': 'text/javascript; charset=UTF-8'
        }

    _ERROR_PREFIX: Final = '<P class="error">'
    _ERROR_SUFFIX: Final = '</P>'

    def __init__(self, server, client):
        """Save the server and client references for use throughout this class. Instantiate
        the main objects that provide functionality for this class."""
        self._server = server
        self._client = client

        self._iexApi: Final = IexApi(self._IEX_API_KEY)
        self._portfolio = Portfolio(self._PORTFOLIO_DB, self._iexApi)

        self._responseBuilder: Final = HttpResponseBuilder(Http.VERSION)
        self._htmlPageBuilder: Final = HtmlPageBuilder()
        self._jsFileBuilder: Final = JsFileBuilder()

        self._routingTableGet: Final = RoutingTable()
        self._routingTablePost: Final = RoutingTable()
        self._addStaticRoutes()

    def start(self):
        """Start the main processor that will service the client connection"""
        _thread.start_new_thread(self._threadEntryPoint, ())

    def _threadEntryPoint(self):
        """
        This is the main routine for providing a service for clients. There is no loop because
        this web server doesn't persist connections. It's expected that each connection will send
        one request, receive a response, then disconnect.
        """

        try:
            # input
            self._client.readRequest()

            # process
            if not self._isPasswordConfigured():
                headers, body = self._makeServiceUnavailable()

            elif self._isEmptyRequest():
                headers, body = self._makeBadRequest()

            elif not self._isAuthorized():
                headers, body = self._makeUnauthorized()

            else:
                headers, body = self._makeResponse()

            # output
            if not isNoneOrEmpty(headers):
                self._client.writeResponse(headers, body)

        except Exception as ex:
            logMessage(f'Exception caught: {ex}')

        finally:
            self._client.disconnect()  # no persistent connections

    def _makeResponse(self):
        """Build a response for the client based upon their request"""
        if not self._areCredentialsValid():
            headers, body = self._makeUnauthorized()  # all requests must have a valid auth header

        elif self._isGet():
            # pass get requests through a routing table
            headers, body = self._routeGetRequest(self._client.getRequest())

        elif self._isPost():
            # pass post requests through a routing table
            headers, body = self._routePostRequest(self._client.getRequest())

        else:
            # all other HTTP method types are not allowed
            headers, body = self._makeMethodNotAllowed()

        # if the above statements couldn't understand what the client is asking for, then
        # we respond accordingly
        if isNoneOrEmpty(headers):
            return self._makeNotFound()

        return headers, body

    def _areCredentialsValid(self):
        """Checks whether an auth header was supplied, and if so, that it's basic auth
        supplied with a matching username and password"""
        auth = self._client.getRequest().getAuthorization()
        if auth is None or len(auth) < 3 or auth[0] != Http.BASIC_AUTH:
            return False

        # we're using a student ID number as the username and password
        return auth[1] == self._server.getPassword() and auth[2] == self._server.getPassword()

    def _isPasswordConfigured(self):
        """Checks for the presence of a password"""
        return not isNoneOrEmpty(self._server.getPassword())  # not mutex protected, but readonly after startup

    def _isEmptyRequest(self):
        """Checks whether any bytes were received from the client"""
        return self._client.getRequest().isEmpty()

    def _isAuthorized(self):
        """Checks for the presence of an auth header"""
        return self._client.getRequest().hasAuthorization()

    def _isGet(self):
        """Returns whether the method type is GET"""
        return self._client.getRequest().getMethod() == Http.GET

    def _isPost(self):
        """Returns whether the method type is POST"""
        return self._client.getRequest().getMethod() == Http.POST

    def _makeBadRequest(self):
        """Builds a standard HTTP 400 response"""
        headers = self._responseBuilder.makeBadRequest()
        body = self._htmlPageBuilder.makeErrorPage(400, None)
        return headers, body

    def _makeUnauthorized(self):
        """Builds a standard HTTP 401 response"""
        headers = self._responseBuilder.makeUnauthorized() + \
                  self._responseBuilder.makeWwwAuthenticate(Http.BASIC_AUTH, self._PORTFOLIO_NAME)
        body = self._htmlPageBuilder.makeErrorPage(401, None)
        return headers, body

    def _makeNotFound(self):
        """Builds a standard HTTP 404 response"""
        headers = self._responseBuilder.makeNotFound()
        body = self._htmlPageBuilder.makeErrorPage(404, None)
        return headers, body

    def _makeMethodNotAllowed(self):
        """Builds a standard HTTP 405 response"""
        headers = self._responseBuilder.makeMethodNotAllowed()
        body = self._htmlPageBuilder.makeErrorPage(405, None)
        return headers, body

    def _makeServiceUnavailable(self):
        """Builds a standard HTTP 503 response"""
        headers = self._responseBuilder.makeServiceUnavailable()
        body = self._htmlPageBuilder.makeErrorPage(503, None)
        return headers, body

    def _addStaticRoutes(self):
        """Inserts routing information that are defined at coding time, not runtime"""
        self._routingTableGet.add('/', self._browseToPortfolio)
        self._routingTableGet.add(self._PORTFOLIO_URI, self._browseToPortfolio)
        self._routingTableGet.add(self._RESEARCH_URI, self._browseToResearch)
        self._routingTableGet.add(JsFileBuilder.COMMON_STOCKS_URI, self._browseToCommonStocks)
        self._routingTableGet.addArbitrary(self._browseToArbitrary)

        self._routingTablePost.add(self._PORTFOLIO_URI, self._updatePortfolio)
        self._routingTablePost.add(self._RESEARCH_URI, self._updateResearch)
        self._routingTablePost.addArbitrary(self._rejectPostRequest)

    def _routeGetRequest(self, request):
        """Passes the request through the GET routing table"""
        return self._routingTableGet.dispatch(request)

    def _routePostRequest(self, request):
        """Passes the request through the POST routing table"""
        return self._routingTablePost.dispatch(request)

    def _browseToPortfolio(self, _):
        """Builds an HTML page representing the current state of the portfolio"""
        return self._makePortfolioPage(self._NO_ERROR)

    def _browseToResearch(self, _):
        """Builds an HTML page representing an empty research page"""
        return self._makeResearchPage(self._NO_ERROR, '', '', self._EMPTY_HTML)

    def _browseToCommonStocks(self, _):
        """Builds a JavaScript array from retrieved stock symbol data"""
        symbols = self._iexApi.fetchCommonStockSymbols()
        headers = self._responseBuilder.makeOK()
        body = self._jsFileBuilder.makeCommonStocksFile(makeJavascriptSymbolArray(symbols))
        return headers, body

    def _browseToArbitrary(self, request):
        """
        This method tries to determine if the request is asking for a file that resides upon
        the web server.
        
        If it does, then that file's contents are sent to the client. If it doesn't, then an
        HTTP 404 response code is sent.
        """
        body = b''
        try:
            fullPath = makeLocalPath(request.getPath())  # convert from a web URI to a local path
            if fullPath is None:
                headers = self._responseBuilder.makeNotFound()

            else:
                headers = self._responseBuilder.makeOK()

                # try to match this file's extension to a mime type that we know about 
                contentType = self._getContentType(fullPath)
                if not isNoneOrEmpty(contentType):
                    headers += contentType

                body = loadFileContents(fullPath)

        except Exception as ex:
            headers = self._responseBuilder.makeInternalServerError()
            body = self._htmlPageBuilder.makeErrorPage(500, str(ex))

        return headers, body

    def _updatePortfolio(self, request):
        """This method adjusts the stocks within the portfolio, but only if the user supplied
        valid values within the web form"""
        form = request.getFormVariables()

        errorMessageHtml = self._validateFormVariables(form)  # run the validation rules
        if not isNoneOrEmpty(errorMessageHtml):
            # build the portfolio page with an error message at the top
            return self._makePortfolioPage(errorMessageHtml)

        # at this point we're reasonably sure the variables within the form have sensible
        # values that we can use to retrieve data from IEX, and build an HTML page.

        self._portfolio.load()
        result = self._portfolio.adjust(form['symbol'],
                                        int(form['quantity']),
                                        float(form['price']) if len(form['price']) > 0 else 0)

        # if that adjustment went well, then we leave the errorMessageHtml variable set
        # to its initial value. Otherwise, we build a simple error message suitable to
        # display upon the web page.

        errorMessageHtml = self._NO_ERROR
        match result:
            case Portfolio.Result.OK:
                self._portfolio.save()  # persist the data to file

            case Portfolio.Result.SYMBOL_NOT_EXISTS:
                errorMessageHtml = self._makeErrorText(
                    f'There is no stock symbol named <I>{form["symbol"]}</I>')

            case Portfolio.Result.DO_NOT_OWN_STOCK:
                errorMessageHtml = self._makeErrorText(
                    f'You do not own any <I>{form["symbol"]}</I> stock')

            case Portfolio.Result.NOT_ENOUGH_STOCK:
                errorMessageHtml = self._makeErrorText(
                    'You cannot sell more stock than you own (i.e. short selling)')

        # build the portfolio page, possibly with an error message at the top
        return self._makePortfolioPage(errorMessageHtml)

    def _makeErrorText(self, errorMessageHtml):
        """Builds a simple HTML happy error message, with a CSS style tag we can use later"""
        return f'{self._ERROR_PREFIX}{errorMessageHtml}{self._ERROR_SUFFIX}'

    def _validateFormVariables(self, form):
        """This method implements the form validation rules for user input"""

        if isAbsentOrEmpty(form, 'symbol'):
            return self._makeErrorText('A <I>symbol</I> was not supplied. This field is required.')

        if isAbsentOrEmpty(form, 'quantity'):
            return self._makeErrorText('A <I>quantity</I> was not supplied. This field is required.')

        if not isInteger(form['quantity'], False):
            return self._makeErrorText('The value supplied for <I>quantity</I> must be an integer.')

        quantity = int(form['quantity'])  # we know it's safe to convert now
        if quantity == 0:
            return self._makeErrorText('The value supplied for <I>quantity</I> must not be zero.')

        if quantity < 0:
            # then the user is selling stock, no need to test the price
            return None

        if isAbsentOrEmpty(form, 'price'):
            return self._makeErrorText('A <I>price</I> was not supplied. This field is required.')

        if not isInteger(form['price'], True) and not isPositiveFloat(form['price']):
            return self._makeErrorText('The value supplied for <I>price</I> must be a positive integer or float.')

        return None

    def _rejectPostRequest(self, _):
        """POST requests are rejected by responding with an HTTP 400 response code"""
        return self._makeBadRequest()

    def _getContentType(self, fullPath):
        """Returns a Content-Type header if the supplied path ends with a well-known file extension,
        returns None otherwise"""
        i = fullPath.rfind('.')
        if i >= 0 and fullPath[i:] in self._fileTypeTable:
            return self._responseBuilder.makeContentType(self._fileTypeTable[fullPath[i:]])

        return None

    def _makePortfolioPage(self, errorMessageHtml):
        """Builds a portfolio page with data loaded from the portfolio file, and from stock quotes
        retrieved from the IEX system"""
        stockHtml = self._makePortfolioStockHtml()
        headers = self._responseBuilder.makeOK()
        body = self._htmlPageBuilder.makePortfolioPage(errorMessageHtml, stockHtml)
        return headers, body

    def _makePortfolioStockHtml(self):
        """
        Loads the portfolio data from disk, then iterates over the data building an HTML row
        tag from each stock

        The IEX system is contacted for a stock quote for each stock within the portfolio. A
        better way to achieve this would be to issue an XHR request from the browser
        """
        if not self._portfolio.load():
            return ''

        html = ''
        for stock in self._portfolio.getAll():
            html += '<TR class="stock-table">' + \
                    f'<TD class="stock-table">{stock["symbol"]}</TD>' + \
                    f'<TD class="stock-table">{stock["quantity"]}</TD>' + \
                    f'<TD class="stock-table">${format(stock["price"], ".2f")}</TD>' + \
                    f'<TD class="stock-table">{self._makeGainOrLossValue(stock["symbol"], stock["price"])}%</TD>' + \
                    '</TR>\n'

        return html

    def _makeGainOrLossValue(self, stockSymbol, oldPrice):
        """Retrieves a current stock quote from the IEX system, then passes that value through
        a simple gain/loss calculation"""
        quote = self._iexApi.fetchQuote(stockSymbol)
        if not isNoneOrEmpty(quote) and quote['latestPrice'] is not None:
            return calculateGainOrLoss(quote['latestPrice'], oldPrice)

        return self._EMPTY_HTML

    def _updateResearch(self, request):
        """Builds a research page that represents currently known information about a specific stock"""
        errorMessageHtml = self._NO_ERROR
        statisticsHtml = self._EMPTY_HTML
        companyNameJs = ''
        dataPointsJs = ''

        form = request.getFormVariables()

        if isAbsentOrEmpty(form, 'stockSymbol'):
            errorMessageHtml = self._makeErrorText('A <I>symbol</I> was not supplied. This field is required.')

        else:
            symbol = form['stockSymbol'].upper()  # ensure a match will occur

            # the page consists of a few pieces of statistical data, and also a graph containing
            # retrieved data points for the stock.

            companyNameJs, statisticsHtml = self._makeStockStatisticsHtml(symbol)
            if statisticsHtml == self._EMPTY_HTML:
                # if this request failed, chances are the request for data points will too. let's
                # not waste asking for those, just build an error message.
                errorMessageHtml = self._makeErrorText(f'No statistics were returned for symbol <I>{symbol}</I>.')

            else:
                dataPointsJs = self._makeChartDataPointsJs(symbol)

        return self._makeResearchPage(errorMessageHtml, companyNameJs, dataPointsJs, statisticsHtml)

    def _makeResearchPage(self, errorMessageHtml, companyNameJs, dataPointsJs, statisticsHtml):
        """Builds a research page with a few pieces of statistical data, and data points
        retrieved from the IEX system"""
        headers = self._responseBuilder.makeOK()
        body = self._htmlPageBuilder.makeResearchPage(errorMessageHtml, companyNameJs, dataPointsJs, statisticsHtml)
        return headers, body

    def _makeStockStatisticsHtml(self, symbol):
        """Retrieves stock statistics from the IEX system, then builds simple HTML paragraphs with
        the data"""
        statistics = self._iexApi.fetchStatistics(symbol)
        if isNoneOrEmpty(statistics):
            return self._EMPTY_HTML

        companyNameJs = statistics['companyName'] if 'companyName' in statistics else ''

        statisticsHtml = f'<P>Symbol: <B>{symbol}</B></P>\n' + \
                         f'<P>Company Name: {statistics["companyName"]}</P>\n' + \
                         f'<P>PE ratio: {format(statistics["peRatio"], ".2f")}</P>\n' + \
                         f'<P>Market Capitalization: {statistics["marketcap"]}</P>\n' + \
                         f'<P>52 week high: {format(statistics["week52high"], ".2f")}</P>\n' + \
                         f'<P>52 week low: {format(statistics["week52low"], ".2f")}</P>\n'

        return companyNameJs, statisticsHtml

    def _makeChartDataPointsJs(self, symbol):
        """Retrieves stock data points from the IEX system, then builds the contents for a
        javascript array with the data"""
        dataPoints = self._iexApi.fetchChartDataPoints(symbol)
        if isNoneOrEmpty(dataPoints):
            return ''

        js = ''
        for dataPoint in dataPoints:
            if 'date' in dataPoint and 'close' in dataPoint:
                js += f'{{ label: "{dataPoint["date"]}", y: {dataPoint["close"]} }},\n'

        return js.rstrip(',')
