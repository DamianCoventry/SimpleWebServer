# 159.352-Web-Dev-Assgn1
Create a simple web server in python.

## Build dependencies
This python script requires python v3.10 or later. Download a copy here https://www.python.org/downloads/

This script uses the `requests` library, and the "handlebars for python" library known as `pybars3`

To install the requests library execute this command `pip install requests` 

To install the pybars3 library execute this command `pip install pybars3`

## Run the web server locally
To run the web server locally execute this command line
`python server.py`. By default, it listens on port `8080`. If you want to use a different
port then create an environment variable named `PORT` with some other positive number.

## Docker container
A `Dockerfile` has been supplied so that this project can be containerised. Change to the
directory with the source files, then execute 
this command line to build the container`docker build -t python-web-server .`

## Run the web server locally from within a container
Execute this command line `docker run -d -p 8080:8080 python-web-server`. Open a web browser
and navigate to `localhost:8080`.

## Push the container to Heroku
After changing to the directory with the source files, execute this sequence of command lines:

`heroku login`

`heroku container:login`

`heroku container:push web --app web-dev-assgn1-159352`

`heroku container:release web --app web-dev-assgn1-159352`

Open a web browser and navigate to https://web-dev-assgn1-159352.herokuapp.com/
