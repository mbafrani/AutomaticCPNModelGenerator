FROM python:3.7.9

COPY . /source-code
RUN apt-get update
RUN apt-get -y upgrade
RUN apt -y install graphviz xdg-utils
RUN pip install -U -r /source-code/requirements.txt

WORKDIR /source-code
EXPOSE 5000

ENTRYPOINT ["python", "./src/app.py"]