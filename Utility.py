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
import sys


def logMessage(message):
    print(message)
    sys.stdout.flush()


def loadFileContents(fileName):
    try:
        file = open(fileName, 'rb')  # read in binary so that \r\n pairs aren't translated to a single \n
        data = file.read()
        file.close()
        return data

    except IOError:
        return None


def makeLocalPath(path):
    fullPath = os.getcwd() + path
    return fullPath if os.path.exists(fullPath) else None


def makeJavascriptSymbolArray(symbols):
    s = ''
    for symbol in symbols:
        if symbol['type'] is not None and symbol['type'] == 'cs' and symbol['symbol'] is not None:
            s += '"' + symbol['symbol'] + '",\n'
    return s.rstrip(",\n")


def calculateStockPrice(oldQuantity, oldPrice, newQuantity, newPrice):
    total = oldQuantity + newQuantity
    return (oldQuantity * oldPrice + newQuantity * newPrice) / total


def calculateGainOrLoss(newPrice, oldPrice):
    return format((newPrice - oldPrice) / oldPrice * 100, '.2f')


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
        f = float(text)
        return f > .0
    except ValueError:
        return False


def isNoneOrEmpty(x):
    return x is None or len(x) == 0
