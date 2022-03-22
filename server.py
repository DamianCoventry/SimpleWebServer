# Requires Python 3.10+
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
from socket import *
from os.path import *
from pybars import Compiler
from typing import Final

import _thread
import base64
import requests
import json

SERVER_TCP_PORT: Final = 8080

MAX_RECEIVED_BYTES: Final = 1024

PORTFOLIO_DATABASE: Final = 'portfolio.json'
PORTFOLIO_PAGE: Final = 'portfolio.html'
PORTFOLIO_URI: Final = '/portfolio'

COMMON_STOCKS_JS: Final = 'commonStocks.js'
COMMON_STOCKS_URI: Final = "/" + COMMON_STOCKS_JS

RESEARCH_PAGE: Final = 'research.html'
RESEARCH_URI: Final = '/research'

HIDE: Final = '&nbsp;'

HTTP_HEADER_200: Final = 'HTTP/1.1 200 OK\r\n\r\n'
HTTP_HEADER_400: Final = 'HTTP/1.1 400 Bad Request\r\n\r\n'
HTTP_HEADER_401: Final = 'HTTP/1.1 401 Unauthorized\r\nWWW-Authenticate: Basic realm=\'Portfolio\'\r\n\r\n'
HTTP_HEADER_404: Final = 'HTTP/1.1 404 Not Found\r\n\r\n'
HTTP_HEADER_405: Final = 'HTTP/1.1 405 Method Not Allowed\r\n\r\n'
HTTP_HEADER_500: Final = 'HTTP/1.1 500 Internal Server Error\r\n\r\n'
HTTP_HEADER_503: Final = 'HTTP/1.1 503 Service Unavailable\r\n\r\n'

HTTP_VERB_GET: Final = 'GET'
HTTP_VERB_POST: Final = 'POST'

IEX_REFERENCE_URI: Final = 'https://cloud.iexapis.com/stable/ref-data/symbols'
IEX_QUOTE_URI: Final = u'https://cloud.iexapis.com/stable/stock/{{stockSymbol}}/quote'
IEX_STATISTICS_URI: Final = u'https://cloud.iexapis.com/stable/stock/{{stockSymbol}}/stats'
IEX_CHART_DATA_URI: Final = u'https://cloud.iexapis.com/stable/stock/{{stockSymbol}}/chart/5y?chartCloseOnly=true'
IEX_PARAM_NAME: Final = 'token'
IEX_PARAM_VALUE: Final = 'pk_069ce437622a4d38aed7a5cc927be3a8'
IEX_PLEASE_UPGRADE_MESSAGE: Final = 'You have used all available credits for the month. Please upgrade ' + \
                                    'or purchase additional packages to access more data.'

ERROR_PREFIX: Final = '<P style="color: red; font-weight: bold;">'
ERROR_SUFFIX: Final = '</P>'


def getFileContents(fileName):
    try:
        file = open(fileName, 'rb')  # read in binary so that \r\n pairs aren't translated to a single \n
        data = file.read()
        file.close()
        return data
    except IOError:
        return None


def loadAndReturnFile(requestUri):
    try:
        fullPath = os.getcwd() + str(requestUri)
        if not exists(fullPath):
            return makeResponse(404, None)

        print('200 OK')
        return HTTP_HEADER_200, getFileContents(fullPath)

    except IOError as e:
        print('loadAndReturnFile: caught [' + str(e) + ']')
    return makeResponse(500, None)


# expecting the file contents to be one student ID number
def getPasswordFromFile():
    return getFileContents('definitelyNotAPasswordFile.txt').decode().strip()


# read the JSON database file into memory
def loadPortfolioData():
    if not exists(PORTFOLIO_DATABASE) or getsize(PORTFOLIO_DATABASE) == 0:
        return []  # valid use case for the first run of the server

    with open(PORTFOLIO_DATABASE) as f:
        return json.load(f)


# writing out the data as JSON, therefore we must use UTF8
def savePortfolioData(portfolio):
    with open(PORTFOLIO_DATABASE, 'w', encoding='utf-8') as f:
        json.dump(portfolio, f, ensure_ascii=False, indent=4)


# returns something like ['GET', '/favicon.ico', 'HTTP/1.1']
def getRequestLine(headerArray):
    return headerArray[0].split()


# returns something like ['Authorization:', 'Basic', 'MjEwMTQxMDc6MjEwMTQxMDc=']
def getHeader(findMe, headerArray):
    for header in headerArray:
        if findMe + ':' in header:
            return header.split()
    return None


# returns a JSON array of objects. View the stock_symbols.js file for example data.
def getAllStockSymbols():
    stockSymbols = requests.get(IEX_REFERENCE_URI + '?' + IEX_PARAM_NAME + '=' + IEX_PARAM_VALUE).text

    if stockSymbols == IEX_PLEASE_UPGRADE_MESSAGE:
        print('using the cached stock symbols')
        return json.loads(getFileContents('stock_symbols.js'))

    return json.loads(stockSymbols)


def generateStockSymbolsJsArray():
    allSecurities = getAllStockSymbols()
    s = ''
    for security in allSecurities:
        if security['type'] is not None and security['type'] == 'cs' and security['symbol'] is not None:
            s += '"' + security['symbol'] + '",\n'
    return s.rstrip(",\n")


# returns a single JSON object. View the stock_quote.js file for example data.
def getStockQuote(stockSymbol):
    uri = generateStockQuoteUri(stockSymbol)
    stockQuote = requests.get(uri + '?' + IEX_PARAM_NAME + '=' + IEX_PARAM_VALUE).text

    if stockQuote == IEX_PLEASE_UPGRADE_MESSAGE:
        print('using the cached stock quote')
        return json.loads(getFileContents('stock_quote.js'))

    return json.loads(stockQuote)


# returns a string representation of a float, to two DP
# formula from page 3 of assignment brief
def calculateGainOrLoss(latestPrice, price):
    return format((latestPrice - price) / price * 100, '.2f')


# retrieve a JSON object from a remote host. if that object contains a 'latestPrice' member then
# use it as input to our gain or loss calculation
def getGainOrLoss(stockSymbol, oldPrice):
    quote = getStockQuote(stockSymbol)
    if quote is not None and quote['latestPrice'] is not None:
        return calculateGainOrLoss(float(quote['latestPrice']), oldPrice)
    return None


# read the portfolio data from disk as a JSON array of objects. generate an HTML table row tag for each object.
def generateStockRows():
    portfolio = loadPortfolioData()
    s = ''
    for stock in portfolio:
        s += '<TR class="stock-table">' + \
             '<TD class="stock-table">' + stock['symbol'] + '</TD>' + \
             '<TD class="stock-table">' + str(stock['quantity']) + '</TD>' + \
             '<TD class="stock-table">$' + format(stock['price'], '.2f') + '</TD>' + \
             '<TD class="stock-table">' + getGainOrLoss(stock['symbol'], stock['price']) + '%</TD>' + \
             '</TR>\n'
    return s


# this function translates a string such as "symbol=JEMD&quantity=1000&price=6.6" into a python map, such as:
# [
#   {'symbol', 'JEMD'},
#   {'quantity', 1000},
#   {'price', 6.6}
# ]
def extractFormVariables(rawFormVariables):
    if rawFormVariables is None:
        return {}

    varNameAndValue = rawFormVariables.split('&')
    if varNameAndValue is None or len(varNameAndValue) == 0:
        return {}

    form = {}
    for nameValue in varNameAndValue:
        nv = nameValue.split('=')
        form[nv[0]] = nv[1]
    return form


# str.isnumeric() can't detect negative numbers
def isInteger(text, testIfPositive):
    try:
        i = int(text)
        if testIfPositive:
            return i > 0
        return True
    except ValueError:
        return False


# str.isdecimal() can't detect negative numbers
def isPositiveFloat(text):
    try:
        float(text)
        return True
    except ValueError:
        return False


# this function implements the business rules:
#   • quantity is a required value
#   • quantity must be an integer
#   • quantity's value be < 0, or > 0, not == 0
#   • price is a required value if quantity meets all of its rules
#   • price must be an integer or float
#   • price's value must be > 0
# a string is returned if a rule is broken, None otherwise
def validateFormVariables(form):
    if form['quantity'] is None or len(form['quantity']) == 0:
        return ERROR_PREFIX + 'A <I>quantity</I> was not supplied. This field is required.' + ERROR_SUFFIX

    if not isInteger(form['quantity'], False):
        return ERROR_PREFIX + 'The value supplied for <I>quantity</I> must be an integer.' + ERROR_SUFFIX

    quantity = int(form['quantity'])  # we know it's safe to convert now
    if quantity == 0:
        return ERROR_PREFIX + 'The value supplied for <I>quantity</I> must not be zero.' + ERROR_SUFFIX

    if quantity < 0:
        # then the user is selling stock, no need to test the price
        return None

    if form['price'] is None or len(form['price']) == 0:
        return ERROR_PREFIX + 'A <I>price</I> was not supplied. This field is required.' + ERROR_SUFFIX

    if not isInteger(form['price'], True) and not isPositiveFloat(form['price']):
        return ERROR_PREFIX + 'The value supplied for <I>price</I> must be a positive integer or float.' + ERROR_SUFFIX

    return None


# remove the stock with the given name from the portfolio
def removePortfolioStock(portfolio, stockSymbol):
    for i in range(len(portfolio)):
        if portfolio[i]['symbol'] == stockSymbol:
            portfolio.pop(i)
            return


# add a new stock to the portfolio. it's possible the user passed in a negative quantity, we handle this case
# by indicating an error
def buyStock(portfolio, symbol, quantity, price):
    if quantity < 0:
        return 'You cannot sell stock that you do not own'

    # check that a stock with this name exists
    if getStockStatistics(symbol) is None:
        return 'No stock exists with the stock symbol <I>' + symbol + '</I>'

    portfolio.append(
        {
            'symbol': symbol,
            'quantity': quantity,
            'price': price
        })
    return None


# this function implements the rules for selling stock
#   • you cannot sell more than you own
#   • if you sell all of your stock, then it's removed from your portfolio
#   • stock price is unaffected by the sale of stock
def sellStock(portfolio, ownedStock, quantityToSell):
    if quantityToSell > ownedStock['quantity']:
        return 'You cannot sell more stock than you own (i.e. short selling)'

    if quantityToSell == ownedStock['quantity']:
        removePortfolioStock(portfolio, ownedStock['symbol'])
    else:
        ownedStock['quantity'] -= quantityToSell

    return None


# returns a floating point number representing the new stock price. the price is the ratio between the old stock's
# value and new stock's value.
# formula from page 6 of assignment brief
def calculateNewPrice(oldQuantity, oldPrice, newQuantity, newPrice):
    total = oldQuantity + newQuantity
    return (oldQuantity * oldPrice + newQuantity * newPrice) / total


# this function implements the rules for adjusting stock of a specific symbol that's already owned. the quantity
# dictates either we're selling, or we're acquiring more of what we already have.
def adjustStock(portfolio, ownedStock, newQuantity, newPrice):
    if newQuantity < 0:
        return sellStock(portfolio, ownedStock, abs(newQuantity))

    ownedStock['price'] = calculateNewPrice(ownedStock['quantity'], ownedStock['price'], newQuantity, newPrice)
    ownedStock['quantity'] += newQuantity
    return None


# this function implements the algorithm for adding, modifying, or deleting stock.
# in this order, the algorithm is:
#   1) extract required inputs from form variables. these were validated for correctness earlier.
#   2) portfolio data are read from disk
#   3) if the form variables identify a stock we don't have, then add it
#   4) if the form variables identify a stock we do have, then either modify it, or delete it
#   5) portfolio data are written to disk
def adjustPortfolio(form):
    stockSymbol = form['symbol'].upper()
    quantity = int(form['quantity'])

    if isInteger(form['price'], True):
        price = int(form['price'])
    elif isPositiveFloat(form['price']):
        price = float(form['price'])
    else:
        price = 0

    portfolio = loadPortfolioData()
    found = False
    
    for stock in portfolio:
        if stock['symbol'] is not None and stock['symbol'] == stockSymbol:
            found = True
            errorMessage = adjustStock(portfolio, stock, quantity, price)
            if errorMessage is not None:
                return errorMessage

    if not found:
        errorMessage = buyStock(portfolio, stockSymbol, quantity, price)
        if errorMessage is not None:
            return errorMessage

    savePortfolioData(portfolio)
    return None


# validate form input variables and bail now if rubbish was supplied by the user
def processPortfolioUpdate(form):
    errorMessage = validateFormVariables(form)
    if errorMessage is not None:
        return generatePortfolioPage(ERROR_PREFIX + errorMessage + ERROR_SUFFIX)

    errorMessage = adjustPortfolio(form)
    if errorMessage is not None:
        return generatePortfolioPage(ERROR_PREFIX + errorMessage + ERROR_SUFFIX)

    return generatePortfolioPage(HIDE)  # the successful return path


# retrieve a JSON object from a remote host. if the user specified a stock symbol that doesn't exist on the
# remote host, then the IEX API returns the text 'Unknown Symbol'
# View the stock_statistics.js file for example data
def getStockStatistics(stockSymbol):
    uri = generateStockStatisticsUri(stockSymbol)
    stockStatistics = requests.get(uri + '?' + IEX_PARAM_NAME + '=' + IEX_PARAM_VALUE).text

    if stockStatistics == IEX_PLEASE_UPGRADE_MESSAGE:
        print('using the cached stock statistics')
        stockStatistics = getFileContents('stock_statistics.js')

    if stockStatistics is None or len(stockStatistics) == 0 or stockStatistics.lower() == 'unknown symbol':
        return None

    return stockStatistics


# generate a reasonable presentation of a few key pieces of statistical data
def generateStatisticsHtml(statisticsJson, stockSymbol):
    return '<P>Symbol: <B>' + stockSymbol + '</B></P>\n' + \
           '<P>Company Name: ' + statisticsJson['companyName'] + '</P>\n' + \
           '<P>PE ratio: ' + format(statisticsJson['peRatio'], '.2f') + '</P>\n' + \
           '<P>Market Capitalization: ' + str(statisticsJson['marketcap']) + '</P>\n' + \
           '<P>52 week high: ' + format(statisticsJson['week52high'], '.2f') + '</P>\n' + \
           '<P>52 week low: ' + format(statisticsJson['week52low'], '.2f') + '</P>\n'


# retrieve a JSON array of objects from a remote host. if the user specified a stock symbol that doesn't
# exist on the remote host, then the IEX API returns the text 'Unknown Symbol'
# View the stock_data_points.js file for example data
def getChartDataPoints(stockSymbol):
    uri = generateChartDataUri(stockSymbol)
    dataPoints = requests.get(uri + '&' + IEX_PARAM_NAME + '=' + IEX_PARAM_VALUE).text

    if dataPoints == IEX_PLEASE_UPGRADE_MESSAGE:
        print('using the cached data points')
        return getFileContents('stock_data_points.js')

    if dataPoints is None or len(dataPoints) == 0 or dataPoints.lower() == 'unknown symbol':
        return None

    return dataPoints


# this function is responsible for generating the HTML the user will see when browsing to the research page.
# the page consists of 3 parts:
#   • a small user input form
#   • a few select pieces of statistical data presented in English
#   • a 2D graph with one data series presented as a spline curve
# note that if the user specified a stock symbol that doesn't exist on the remote host, then the IEX API
# returns the text 'Not Found'
def processResearchRequest(form):
    if form is None or form['stockSymbol'] is None or len(form['stockSymbol']) == 0:
        errorMessage = ERROR_PREFIX + 'A <I>symbol</I> was not supplied. This field is required.' + ERROR_SUFFIX
        return generateResearchPage(HIDE, '', '', errorMessage)

    stockSymbol = form['stockSymbol'].upper()

    # retrieve the statistics as a string
    statistics = getStockStatistics(stockSymbol)
    if statistics is None or statistics.lower() == 'not found':
        statisticsHtml = '<P>No statistics were returned for symbol <B>' + stockSymbol + '</B></P>'
        return generateResearchPage(statisticsHtml, '', '', HIDE)

    # parse the string into a JSON object
    statisticsJson = json.loads(statistics)
    if statisticsJson is None or len(statisticsJson) == 0:
        statisticsHtml = '<P>No statistics were returned for symbol <B>' + stockSymbol + '</B></P>'
        return generateResearchPage(statisticsHtml, '', '', HIDE)

    # use the JSON object to generate HTML
    statisticsHtml = generateStatisticsHtml(statisticsJson, stockSymbol)

    # retrieve a JSON array of objects that represent data points for the stock over time
    dataPointsJs = ''
    dataPoints = getChartDataPoints(stockSymbol)

    # if there were none, or the input datum was rubbish, then the graph will be displayed to the user
    # without a visible spline curve. this is a valid use case.
    if dataPoints is not None:
        dataPointsJson = json.loads(dataPoints)
        # convert to JavaScript syntax
        for dataPoint in dataPointsJson:
            dataPointsJs += '{ label: "' + dataPoint['date'] + '", y: ' + str(dataPoint['close']) + ' },\n'
        dataPointsJs = dataPointsJs.rstrip(',')

    return generateResearchPage(statisticsHtml, statisticsJson['companyName'], dataPointsJs, HIDE)


# this is for developer convenience
def makeResponse(httpCode, parameter):
    match httpCode:
        case 200:
            return HTTP_HEADER_200, None
        case 400:
            print('400 Bad Request')
            return HTTP_HEADER_400, getFileContents('400.html')
        case 401:
            print('401 Unauthorized')
            return HTTP_HEADER_401, getFileContents('401.html')
        case 404:
            print('404 Not Found')
            return HTTP_HEADER_404, getFileContents('404.html')
        case 405:
            print('405 Method Not Allowed')
            return HTTP_HEADER_405, getFileContents('405.html')
        case 503:
            print('503 Service Unavailable')
            return HTTP_HEADER_503, getFileContents('503.html')
        case _:
            print('500 Internal Server Error')
            return HTTP_HEADER_500, generateHttp500Page(parameter).encode()


# this function is the main HTTP handler for the web server. it validates input, handles authentication, and
# directs the flow of the script to the correct subsidiary code
def processHttpRequest(password, request):
    if request is None:
        return makeResponse(400, None)

    requestHeaders = request.decode().splitlines(False)  # convert the text to an array of text lines
    if requestHeaders is None or len(requestHeaders) < 1:
        return makeResponse(400, None)

    requestLine = getRequestLine(requestHeaders)  # parse the first line
    if requestLine is None or len(requestLine) < 3:
        return makeResponse(400, None)
    if requestLine[0] != HTTP_VERB_GET and requestLine[0] != HTTP_VERB_POST:  # GET and POST only
        return makeResponse(405, None)

    print(requestLine[0] + " " + requestLine[1])

    # the request must use basic authorisation
    authorization = getHeader('Authorization', requestHeaders)
    if authorization is None or len(authorization) < 3 or authorization[1] != 'Basic':
        return makeResponse(401, None)

    # crack the password and be sure it matches our expectations
    credentials = base64.b64decode(authorization[2]).decode().split(':')
    if credentials is None or len(credentials) < 2:
        return makeResponse(401, None)
    if credentials[0] != password or credentials[1] != password:
        return makeResponse(401, None)

    try:
        responseHeaders, responseBody = makeResponse(200, None)

        if requestLine[0] == HTTP_VERB_GET:

            if requestLine[1] == RESEARCH_URI:
                # return the mostly empty research page
                responseBody = generateResearchPage(HIDE, '', '', HIDE).encode()
                print('200 OK')
            elif requestLine[1] == "/" or requestLine[1] == PORTFOLIO_URI:
                # load the portfolio, format it, then return it
                responseBody = generatePortfolioPage(HIDE).encode()
                print('200 OK')
            elif requestLine[1] == COMMON_STOCKS_URI:
                # retrieve the common stocks, then generate a JavaScript array from their names
                responseBody = generateCommonStocksJs().encode()
                print('200 OK')
            else:
                responseHeaders, responseBody = loadAndReturnFile(requestLine[1])

        elif requestLine[0] == HTTP_VERB_POST:

            form = extractFormVariables(requestHeaders[len(requestHeaders) - 1])
            if requestLine[1] == RESEARCH_URI:
                # retrieve the stock statistics, then build a research page from them
                responseBody = processResearchRequest(form).encode()
                print('200 OK')
            elif requestLine[1] == PORTFOLIO_URI:
                # add, modify, or delete to/from the stock portfolio, then build a portfolio page from them
                responseBody = processPortfolioUpdate(form).encode()
                print('200 OK')
            else:
                responseHeaders, responseBody = makeResponse(400, None)

    except Exception as e:
        return makeResponse(500, str(e))

    return responseHeaders, responseBody


# this function provides a path that guarantees the socket will be closed
def processTcpConnection(remoteSocket):
    try:
        receivedBytes = remoteSocket.recv(MAX_RECEIVED_BYTES)
        if len(receivedBytes) > 0:
            headers, body = processHttpRequest(passwordFromFile, receivedBytes)
            remoteSocket.send(headers.encode())
            if body is not None:
                remoteSocket.send(body)

    except Exception as e:
        print('processTcpConnection: caught [' + str(e) + ']')

    remoteSocket.close()


# configure a TCP socket for listening
serverPort = SERVER_TCP_PORT
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(1)

# create a text template compiler
pybars = Compiler()

# build a set of text templates
http500Page = pybars.compile(getFileContents('500.html').decode('UTF-8'))
portfolioPage = pybars.compile(getFileContents(PORTFOLIO_PAGE).decode('UTF-8'))
commonStocksJs = pybars.compile(getFileContents(COMMON_STOCKS_JS).decode('UTF-8'))
stockQuoteUri = pybars.compile(IEX_QUOTE_URI)
researchPage = pybars.compile(getFileContents(RESEARCH_PAGE).decode('UTF-8'))
stockStatisticsUri = pybars.compile(IEX_STATISTICS_URI)
chartDataUri = pybars.compile(IEX_CHART_DATA_URI)


# a simple 500 internal error page that indicates why the server puked
def generateHttp500Page(errorMessage):
    return http500Page({'errorMessage': errorMessage})


# creates a stock quote URI on the fly from a stock symbol
def generateStockQuoteUri(stockSymbol):
    return stockQuoteUri({'stockSymbol': stockSymbol})


# creates a stock statistics URI on the fly from a stock symbol
def generateStockStatisticsUri(stockSymbol):
    return stockStatisticsUri({'stockSymbol': stockSymbol})


# creates a chart data URI on the fly from a stock symbol
def generateChartDataUri(stockSymbol):
    return chartDataUri({'stockSymbol': stockSymbol})


# the portfolio page shows what stocks are available to buy, shows all stocks currently bought, and displays
# an optional error message
def generatePortfolioPage(errorMessage):
    return portfolioPage(
        {
            'stockRows': generateStockRows(),
            'errorMessage': errorMessage
        })


def generateCommonStocksJs():
    return commonStocksJs({'stockSymbols': generateStockSymbolsJsArray()})


# the research page is originally presented devoid of all data. the user must enter a stock symbol and submit it.
# this server responds by retrieving statistics for that stock, then generating HTML on the fly from some of those
# statistics. this server also retrieves data points for the stock for use in a client side graph. finally, the
# research page can display an error message.
def generateResearchPage(stockStatistics, companyName, dataPoints, errorMessage):
    return researchPage(
        {
            'stockStatistics': stockStatistics,
            'companyName': companyName,
            'dataPoints': dataPoints,
            'errorMessage': errorMessage
        })


passwordFromFile = getPasswordFromFile()

print('The server is ready to receive HTTP requests.')

while True:
    clientSocket, address = serverSocket.accept()

    if passwordFromFile is None:
        # we're not going to provide a service without basic authentication configured
        clientSocket.send(HTTP_HEADER_503.encode())
        clientSocket.send(getFileContents('503.html'))
        clientSocket.close()
    else:
        _thread.start_new_thread(processTcpConnection, (clientSocket,))
