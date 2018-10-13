FROM ubuntu:18.04

ENV DEBIAN_FRONTEND=noninteractive
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# Install 
RUN apt-get update && apt-get install -y python3-pip python3-vtk7

# Install Pipenv:
RUN pip3 install pipenv

# Install requirements
COPY Pipfile /tmp/Pipfile
COPY Pipfile.lock /tmp/Pipfile.lock
RUN set -ex && cd /tmp && pipenv install --deploy --system

# Set up non-root user
ARG NB_USER=appuser
ARG NB_UID=1000
RUN useradd -m -u ${NB_UID} -s /sbin/nologin ${NB_USER}

USER ${NB_USER}
WORKDIR /home/${NB_USER}

COPY config.yml.j2 config.yml.j2

COPY kevlar_mesher kevlar_mesher

CMD python3 -m kevlar_mesher -c config.yml.j2