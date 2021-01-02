FROM python:3

WORKDIR /usr/src/app
COPY src Makefile requirements.txt ./

RUN make init

EXPOSE 5000

CMD [ "python", "src/app.py" ]