FROM ubuntu:bionic-20210325
RUN apt update && \
    apt install -y software-properties-common && \
    add-apt-repository -y ppa:deadsnakes/ppa && \
    apt update && \
    apt install -y python3.8 python3.8-venv python3.8-dev python3-pip gcc
WORKDIR /opt/
CMD ["/bin/bash"]
