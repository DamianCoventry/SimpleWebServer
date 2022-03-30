import json
import os
from enum import Enum
from Utility import calculateStockPrice


class Portfolio:
    def __init__(self, fileName, iexApi):
        self._fileName = fileName
        self._iexApi = iexApi
        self._stocks = None

    def getAll(self):
        return self._stocks

    def load(self):
        if os.path.exists(self._fileName) and os.path.getsize(self._fileName) > 0:
            with open(self._fileName) as f:
                self._stocks = json.load(f)

        return self._stocks is not None

    def save(self):
        if self._stocks is None:
            return False

        with open(self._fileName, 'w', encoding='utf-8') as f:
            json.dump(self._stocks, f, ensure_ascii=False, indent=4)

        return True

    class Result(Enum):
        OK = 1
        SYMBOL_NOT_EXISTS = 2
        DO_NOT_OWN_STOCK = 3
        NOT_ENOUGH_STOCK = 4

    def adjust(self, symbol, quantity, price):
        symbol = symbol.upper()
        if quantity < 0:
            if self._isOwned(symbol):
                return self._sell(symbol, abs(quantity))
            return self.Result.DO_NOT_OWN_STOCK

        if self._isOwned(symbol):
            return self._buyMore(symbol, quantity, price)

        return self._buy(symbol, quantity, price)

    def _isOwned(self, symbol):
        if self._stocks is None:
            return False

        for stock in self._stocks:
            if 'symbol' in stock and stock['symbol'].upper() == symbol:
                return True

        return False

    def _buy(self, symbol, quantity, price):
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
        stock = self._get(symbol)
        
        if quantity > stock['quantity']:
            return self.Result.NOT_ENOUGH_STOCK

        if quantity == stock['quantity']:
            self._remove(symbol)
        else:
            stock['quantity'] -= quantity

        return self.Result.OK

    def _existsRemotely(self, symbol):
        return self._iexApi.fetchStatistics(symbol) is not None

    def _remove(self, symbol):
        for i in range(len(self._stocks)):
            if self._stocks[i]['symbol'] == symbol:
                self._stocks.pop(i)
                return

    def _get(self, symbol):
        for i in range(len(self._stocks)):
            if self._stocks[i]['symbol'] == symbol:
                return self._stocks[i]
        return None
