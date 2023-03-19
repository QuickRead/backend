FROM python:latest

ENV CONTAINER_HOME=/var/www

ADD . $CONTAINER_HOME
WORKDIR $CONTAINER_HOME

RUN pip install -U pip & pip install -r $CONTAINER_HOME/requirements.txt