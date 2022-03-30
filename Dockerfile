FROM python:3.10-alpine3.15

WORKDIR /usr/src/app

RUN python3 -m pip install --no-cache-dir -q pybars3
RUN python3 -m pip install --no-cache-dir -q requests

COPY . /usr/src/app

# Heroku doesn't use this
EXPOSE 8080/tcp

CMD [ "python3", "Main.py" ]
