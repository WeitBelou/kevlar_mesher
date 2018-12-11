FROM ubuntu:18.04

ENV DEBIAN_FRONTEND noninteractive
ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

RUN apt-get update && apt-get install -y python3-pip python3-vtk7

ADD requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt

ADD kevlar_mesher kevlar_mesher
ADD config.yml.j2 config.yml.j2

CMD python3 -m kevlar_mesher -c config.yml.j2