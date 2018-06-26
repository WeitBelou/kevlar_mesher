Bootstrap: docker
From: ubuntu:18.04

%post
    apt-get update
    apt-get install -y python3 python3-pip python3-vtk7
    pip3 install -r /tmp/requirements.txt

%files
    requirements.txt /tmp/requirements.txt
    kevlar_mesher kevlar_mesher
    config.yaml config.yaml

% environment
    DEBIAN_FRONTEND noninteractive

%runscript
    python3 -m kevlar_mesher -c config.yaml
