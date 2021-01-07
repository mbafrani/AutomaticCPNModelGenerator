FROM python:3.8

WORKDIR /usr/src/app
COPY src Makefile requirements.txt ./

RUN make linux-graphviz && make init

EXPOSE 5000

CMD [ "python", "app.py" ]