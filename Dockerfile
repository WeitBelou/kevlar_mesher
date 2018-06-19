FROM python:3.6

ADD requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

RUN mkdir /app
WORKDIR /app

ADD kevlar_mesher kevlar_mesher
ADD config.yaml config.yaml

ADD docker/run.sh run.sh

CMD ./run.sh
