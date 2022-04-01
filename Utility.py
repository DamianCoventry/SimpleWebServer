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
    """
    Simple wrapper that forces a flush of stdout after each call to print. If we don't do
    this, then Heroku's logging system won't see our output until the internal stdout buffer
    is full, then auto-flushed
    """
    print(message)
    sys.stdout.flush()


def loadFileContents(fileName):
    """
    Simple file open+read+close wrapper that allows the caller to have a one-liner 'get me
    all data from file' statement. Note that this function swallows all file i/o exceptions
    and simply returns None for ALL error cases.
    """
    try:
        file = open(fileName, 'rb')  # read in binary so that \r\n pairs aren't translated to a single \n
        data = file.read()
        file.close()
        return data

    except IOError:
        return None


def makeLocalPath(path):
    """
    Makes a full path from the current working directory and the passed in argument. This assumes the
    argument begins with a '/' character.
    If this full path represents a valid file system item, then the full path is returned, otherwise
    None is returned
    """
    fullPath = os.getcwd() + path
    return fullPath if os.path.exists(fullPath) else None


def makeJavascriptSymbolArray(symbols):
    """Makes a CSV string from the passed in argument's data. This assumes the argument is something
    capable of being iterated, and that the item at each iteration has keys 'type' and 'symbol'"""
    s = ''
    for symbol in symbols:
        if not isNoneOrEmpty(symbol['type']) and symbol['type'] == 'cs' and not isNoneOrEmpty(symbol['symbol']):
            s += '"' + symbol['symbol'] + '",\n'
    return s.rstrip(",\n")


def calculateStockPrice(oldQuantity, oldPrice, newQuantity, newPrice):
    """Executes the formula for calculating a stock price"""
    total = oldQuantity + newQuantity
    return (oldQuantity * oldPrice + newQuantity * newPrice) / total


def calculateGainOrLoss(newPrice, oldPrice):
    """Executes the formula for calculating a gain/loss percentage"""
    return format((newPrice - oldPrice) / oldPrice * 100, '.2f')


def isInteger(text, testIfPositive):
    """Determines if the passed in text represents an integer. str.isnumeric() was unable to
    answer this question"""
    try:
        i = int(text)
        if testIfPositive:
            return i > 0
        return True
    except ValueError:
        return False


def isPositiveFloat(text):
    """Determines if the passed in text represents a positive floating point number. str.isdecimal()
    was unable to answer this question"""
    try:
        f = float(text)
        return f > .0
    except ValueError:
        return False


def isNoneOrEmpty(x):
    """Syntactic sugar for developer convenience"""
    return x is None or len(x) == 0


def isAbsentOrEmpty(form, value):
    """Syntactic sugar for developer convenience"""
    return value not in form or isNoneOrEmpty(form[value])
