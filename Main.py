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
from Utility import logMessage
from WebServer import WebServer

os.environ['PYTHONUNBUFFERED'] = "1"

try:
    # create an instance of the server, then start listening for connections.
    server = WebServer(os.environ.get('PORT'))  # use Heroku's port number
    server.listen()

except Exception as ex:
    logMessage(f'Exception caught: {ex}')

finally:
    logMessage('Server stopped')
