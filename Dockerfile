FROM python:3

WORKDIR /usr/src/app

RUN python3 -m pip install --no-cache-dir -q pybars3
RUN python3 -m pip install --no-cache-dir -q requests

COPY . .

# Heroku doesn't use this
EXPOSE 8080/tcp

CMD [ "python3", "./server.py" ]
