FROM ubuntu:18.04

RUN apt-get update -y && apt-get install -y python3-pip python3-dev git gcc g++

WORKDIR /src

COPY ./requirements.txt /src/requirements.txt
COPY ./config/logging/local.conf /src/local.conf

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

COPY . /src

ENTRYPOINT ["python3"]