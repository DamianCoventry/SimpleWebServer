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
from enum import Enum
from Utility import *


class Portfolio:
    """
    This class stores the current state of the portfolio. The portfolio represents the currently
    purchased stocks.

    There's only a few public methods on this class, the bulk of the work is adjusting the portfolio
    within private methods.
    """

    def __init__(self, fileName, iexApi):
        """Save the arguments for later use. Give the stock container a name."""
        self._fileName = fileName
        self._iexApi = iexApi
        self._stocks = None

    def getAll(self):
        """Returns a reference to the stock container so that it can be iterated over to build HTML"""
        return self._stocks

    def load(self):
        """Opens the backing file for the purchased stock data, then reads the data into a container.
        Returns true if data were read, false otherwise"""
        if os.path.exists(self._fileName) and os.path.getsize(self._fileName) > 0:
            with open(self._fileName) as f:
                self._stocks = json.load(f)

        return not isNoneOrEmpty(self._stocks)

    def save(self):
        """Opens the backing file for the purchased stock data, then writes data from the container into it.
        Returns true if data were written, false otherwise"""
        if isNoneOrEmpty(self._stocks):
            return False

        with open(self._fileName, 'w', encoding='utf-8') as f:
            json.dump(self._stocks, f, ensure_ascii=False, indent=4)

        return True

    class Result(Enum):
        """Represents the possible outcomes from adjusting the stock portfolio"""
        OK = 1
        SYMBOL_NOT_EXISTS = 2
        DO_NOT_OWN_STOCK = 3
        NOT_ENOUGH_STOCK = 4

    def adjust(self, symbol, quantity, price):
        """
        This is the main routine for adjusting the stock portfolio based upon the user's input
        from a web form.

        There's a few possible outcomes from this routine, each is represented by a value from
        the Result enum. It's expected the consumer of this enum return value will implement a
        switch/case to handle the use cases.
        """

        symbol = symbol.upper()  # ensure a match will occur

        if quantity < 0:  # is the user trying to sell stock?
            if self._isOwned(symbol):
                return self._sell(symbol, abs(quantity))  # selling existing stock. Note the call to abs()

            return self.Result.DO_NOT_OWN_STOCK  # can't sell what you don't own

        # at this point we're sure the user is trying to buy stock

        if self._isOwned(symbol):
            return self._buyMore(symbol, quantity, price)  # accumulate existing stock

        return self._buy(symbol, quantity, price)  # add new stock to the portfolio

    def _isOwned(self, symbol):
        """Determines if the argument is the symbol for a stock we're storing in our container"""
        if isNoneOrEmpty(self._stocks):
            return False

        for stock in self._stocks:
            if 'symbol' in stock and stock['symbol'].upper() == symbol:  # ensure a match will occur
                return True

        return False

    def _buy(self, symbol, quantity, price):
        """Implements the purchasing logic for a stock we don't have in our container. The only
        rule is that the symbol passed in must exist on the remote host serving up the symbols."""
        if not self._existsRemotely(symbol):
            return self.Result.SYMBOL_NOT_EXISTS

        self._stocks.append(
            {
                'symbol': symbol,
                'quantity': quantity,
                'price': price
            })
        return self.Result.OK

    def _buyMore(self, symbol, newQuantity, newPrice):
        """
        Implements the purchasing logic for a stock we already have in our container.

        The symbol passed in must exist on the remote host serving up the symbols, and we run a
        simple formula that adjusts the price for this stock within our container.

        The formula basically calculates the ratio between the old price and the new price. Over
        time this produces an averaging effect on the price, as each adjustment is based upon the
        previously calculated ratio.
        """

        if not self._existsRemotely(symbol):
            return self.Result.SYMBOL_NOT_EXISTS

        stock = self._get(symbol)

        oldQuantity = stock['quantity']
        oldPrice = stock['price']

        adjustedPrice = calculateStockPrice(oldQuantity, oldPrice, newQuantity, newPrice)

        stock['price'] = adjustedPrice
        stock['quantity'] += newQuantity

        return self.Result.OK

    def _sell(self, symbol, quantity):
        """
        Implements the logic for selling an owned stock. It is assumed that quantity was converted
        to a positive number before being passed in.

        If the user sells all of their stock, then it's removed from the stock container.
        """
        stock = self._get(symbol)
        
        if quantity > stock['quantity']:
            return self.Result.NOT_ENOUGH_STOCK  # you cannot sell more stock than you own

        if quantity == stock['quantity']:
            self._remove(symbol)  # get rid of its state
        else:
            stock['quantity'] -= quantity  # simply reduce the value

        return self.Result.OK

    def _existsRemotely(self, symbol):
        """Ask the IEX system if they've heard of this symbol"""
        return self._iexApi.fetchStatistics(symbol) is not None

    def _remove(self, symbol):
        """Remove state represented by the passed in symbol"""
        for i in range(len(self._stocks)):
            if self._stocks[i]['symbol'] == symbol:
                self._stocks.pop(i)
                return

    def _get(self, symbol):
        """Returns a reference to the stock represented by the passed in symbol"""
        for i in range(len(self._stocks)):
            if self._stocks[i]['symbol'] == symbol:
                return self._stocks[i]

        return None
