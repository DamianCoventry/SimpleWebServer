#
# Designed and written by Damian Coventry
# Copyright (c) 2022, all rights reserved
#
# Massey University
# 159.352 Advanced Web Development
# Assignment 1
# 2022 Semester 1
#

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
    _PORTFOLIO_NAME: Final = 'portfolio'
    _PORTFOLIO_URI: Final = f'/{_PORTFOLIO_NAME}'
    _PORTFOLIO_DB: Final = f'portfolioDatabase/{_PORTFOLIO_NAME}.json'

    _RESEARCH_NAME: Final = 'research'
    _RESEARCH_URI: Final = f'/{_RESEARCH_NAME}'

    _NO_ERROR: Final = '&nbsp;'
    _EMPTY_HTML: Final = '&nbsp;'

    _IEX_API_KEY: Final = 'pk_069ce437622a4d38aed7a5cc927be3a8'

    _fileTypeTable: Final =\
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
        self._server = server
        self._client = client

        self._iexApi: Final = IexApi(self._IEX_API_KEY)
        self._portfolio = Portfolio(self._PORTFOLIO_DB, self._iexApi)

        self._responseBuilder: Final = HttpResponseBuilder(Http.VERSION, Http.HEADER_SEP)
        self._htmlPageBuilder: Final = HtmlPageBuilder()
        self._jsFileBuilder: Final = JsFileBuilder()

        self._routingTableGet: Final = RoutingTable()
        self._routingTablePost: Final = RoutingTable()
        self._addStaticRoutes()

    def start(self):
        _thread.start_new_thread(self._threadEntryPoint, ())

    def _threadEntryPoint(self):
        try:
            self._client.readRequest()

            if not self._isPasswordConfigured():
                headers, body = self._makeServiceUnavailable()

            elif self._isEmptyRequest():
                headers, body = self._makeBadRequest()

            elif not self._isAuthorized():
                headers, body = self._makeUnauthorized()

            else:
                headers, body = self._makeResponse()

            if headers is not None:
                self._client.writeResponse(headers, body)

        except Exception as ex:
            logMessage(f'Exception caught: {ex}')

        finally:
            self._client.disconnect()  # no persistent connections

    def _makeResponse(self):
        if not self._areCredentialsValid():
            headers, body = self._makeUnauthorized()

        elif self._isGet():
            headers, body = self._routeGetRequest(self._client.getRequest())

        elif self._isPost():
            headers, body = self._routePostRequest(self._client.getRequest())

        else:
            headers, body = self._makeMethodNotAllowed()

        if isNoneOrEmpty(headers):
            return self._makeNotFound()

        return headers, body

    def _areCredentialsValid(self):
        auth = self._client.getRequest().getAuthorization()
        if auth is None or len(auth) < 3 or auth[0] != Http.BASIC_AUTH:
            return False
        return auth[1] == self._server.getPassword() and auth[2] == self._server.getPassword()

    def _isPasswordConfigured(self):
        return self._server.getPassword() is not None  # not mutex protected, but readonly after startup

    def _isEmptyRequest(self):
        return self._client.getRequest().isEmpty()

    def _isAuthorized(self):
        return self._client.getRequest().hasAuthorization()

    def _isGet(self):
        return self._client.getRequest().getMethod() == Http.GET

    def _isPost(self):
        return self._client.getRequest().getMethod() == Http.POST

    def _makeBadRequest(self):
        headers = self._responseBuilder.makeBadRequest()
        body = self._htmlPageBuilder.makeErrorPage(400, None)
        return headers, body

    def _makeUnauthorized(self):
        headers = self._responseBuilder.makeUnauthorized() + \
                  self._responseBuilder.makeWwwAuthenticate(Http.BASIC_AUTH, self._PORTFOLIO_NAME)
        body = self._htmlPageBuilder.makeErrorPage(401, None)
        return headers, body

    def _makeNotFound(self):
        headers = self._responseBuilder.makeNotFound()
        body = self._htmlPageBuilder.makeErrorPage(404, None)
        return headers, body

    def _makeMethodNotAllowed(self):
        headers = self._responseBuilder.makeMethodNotAllowed()
        body = self._htmlPageBuilder.makeErrorPage(405, None)
        return headers, body

    def _makeServiceUnavailable(self):
        headers = self._responseBuilder.makeServiceUnavailable()
        body = self._htmlPageBuilder.makeErrorPage(503, None)
        return headers, body

    def _addStaticRoutes(self):
        self._routingTableGet.add('/', self._browseToPortfolio)
        self._routingTableGet.add(self._PORTFOLIO_URI, self._browseToPortfolio)
        self._routingTableGet.add(self._RESEARCH_URI, self._browseToResearch)
        self._routingTableGet.add(JsFileBuilder.COMMON_STOCKS_URI, self._browseToCommonStocks)
        self._routingTableGet.addArbitrary(self._browseToArbitrary)

        self._routingTablePost.add(self._PORTFOLIO_URI, self._updatePortfolio)
        self._routingTablePost.add(self._RESEARCH_URI, self._updateResearch)
        self._routingTablePost.addArbitrary(self._rejectPostRequest)

    def _routeGetRequest(self, request):
        return self._routingTableGet.dispatch(request)

    def _routePostRequest(self, request):
        return self._routingTablePost.dispatch(request)

    def _browseToPortfolio(self, _):
        return self._makePortfolioPage(self._NO_ERROR)

    def _browseToResearch(self, _):
        return self._makeResearchPage(self._NO_ERROR, '', '', self._EMPTY_HTML)

    def _browseToCommonStocks(self, _):
        symbols = self._iexApi.fetchSymbols()
        headers = self._responseBuilder.makeOK()
        body = self._jsFileBuilder.makeCommonStocksFile(makeJavascriptSymbolArray(symbols))
        return headers, body

    def _browseToArbitrary(self, request):
        body = b''
        try:
            fullPath = makeLocalPath(request.getPath())
            if fullPath is None:
                headers = self._responseBuilder.makeNotFound()

            else:
                headers = self._responseBuilder.makeOK()

                contentType = self._getContentType(fullPath)
                if contentType is not None:
                    headers += contentType

                body = loadFileContents(fullPath)

        except Exception as ex:
            headers = self._responseBuilder.makeInternalServerError()
            body = self._htmlPageBuilder.makeErrorPage(500, str(ex))

        return headers, body

    def _updatePortfolio(self, request):
        form = request.getFormVariables()

        errorMessage = self._validateFormVariables(form)
        if errorMessage is not None:
            return self._makePortfolioPage(errorMessage)

        self._portfolio.load()
        result = self._portfolio.adjust(form['symbol'],
                                        int(form['quantity']),
                                        float(form['price']) if len(form['price']) > 0 else 0)

        errorMessage = self._NO_ERROR
        match result:
            case Portfolio.Result.OK:
                self._portfolio.save()

            case Portfolio.Result.SYMBOL_NOT_EXISTS:
                errorMessage = self._makeErrorText(
                    f'There is no stock symbol named <I>{form["symbol"]}</I>')

            case Portfolio.Result.DO_NOT_OWN_STOCK:
                errorMessage = self._makeErrorText(
                    f'You do not own any <I>{form["symbol"]}</I> stock')

            case Portfolio.Result.NOT_ENOUGH_STOCK:
                errorMessage = self._makeErrorText(
                    'You cannot sell more stock than you own (i.e. short selling')

        return self._makePortfolioPage(errorMessage)

    def _makeErrorText(self, errorMessage):
        return self._ERROR_PREFIX + errorMessage + self._ERROR_SUFFIX

    def _validateFormVariables(self, form):
        if 'symbol' not in form or len(form['symbol']) == 0:
            return self._makeErrorText('A <I>symbol</I> was not supplied. This field is required.')

        if 'quantity' not in form or len(form['quantity']) == 0:
            return self._makeErrorText('A <I>quantity</I> was not supplied. This field is required.')

        if not isInteger(form['quantity'], False):
            return self._makeErrorText('The value supplied for <I>quantity</I> must be an integer.')

        quantity = int(form['quantity'])  # we know it's safe to convert now
        if quantity == 0:
            return self._makeErrorText('The value supplied for <I>quantity</I> must not be zero.')

        if quantity < 0:
            # then the user is selling stock, no need to test the price
            return None

        if 'price' not in form or len(form['price']) == 0:
            return self._makeErrorText('A <I>price</I> was not supplied. This field is required.')

        if not isInteger(form['price'], True) and not isPositiveFloat(form['price']):
            return self._makeErrorText('The value supplied for <I>price</I> must be a positive integer or float.')

        return None

    def _rejectPostRequest(self, _):
        return self._makeBadRequest()

    def _getContentType(self, fullPath):
        i = fullPath.rfind('.')
        if i >= 0 and fullPath[i:] in self._fileTypeTable:
            return self._responseBuilder.makeContentType(self._fileTypeTable[fullPath[i:]])

        return None

    def _makePortfolioPage(self, errorMessage):
        stockHtml = self._makePortfolioStockHtml()
        headers = self._responseBuilder.makeOK()
        body = self._htmlPageBuilder.makePortfolioPage(errorMessage, stockHtml)
        return headers, body

    def _makePortfolioStockHtml(self):
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
        quote = self._iexApi.fetchQuote(stockSymbol)
        if quote is not None and quote['latestPrice'] is not None:
            return calculateGainOrLoss(float(quote['latestPrice']), oldPrice)
        
        return self._EMPTY_HTML

    def _updateResearch(self, request):
        errorMessage = self._NO_ERROR
        statisticsHtml = self._EMPTY_HTML
        companyNameJs = ''
        dataPointsJs = ''

        form = request.getFormVariables()

        if 'stockSymbol' not in form or len(form['stockSymbol']) == 0:
            errorMessage = self._makeErrorText('A <I>symbol</I> was not supplied. This field is required.')

        else:
            symbol = form['stockSymbol'].upper()

            companyNameJs, statisticsHtml = self._makeStockStatisticsHtml(symbol)
            if statisticsHtml == self._EMPTY_HTML:
                errorMessage = self._makeErrorText(f'No statistics were returned for symbol <I>{symbol}</I>.')
            else:
                dataPointsJs = self._makeChartDataPointsJs(symbol)

        return self._makeResearchPage(errorMessage, companyNameJs, dataPointsJs, statisticsHtml)

    def _makeResearchPage(self, errorMessage, companyNameJs, dataPointsJs, statisticsHtml):
        headers = self._responseBuilder.makeOK()
        body = self._htmlPageBuilder.makeResearchPage(errorMessage, companyNameJs, dataPointsJs, statisticsHtml)
        return headers, body

    def _makeStockStatisticsHtml(self, symbol):
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
        dataPoints = self._iexApi.fetchChart(symbol)
        if isNoneOrEmpty(dataPoints):
            return ''

        js = ''
        for dataPoint in dataPoints:
            if 'date' in dataPoint and 'close' in dataPoint:
                js += f'{{ label: "{dataPoint["date"]}", y: {dataPoint["close"]} }},\n'
        
        return js.rstrip(',')
