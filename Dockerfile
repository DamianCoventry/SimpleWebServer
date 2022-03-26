FROM python:3

WORKDIR /usr/src/app

RUN pip install pybars3
RUN pip install requests

COPY . .

EXPOSE 8080/tcp

CMD [ "python", "./server.py" ]
