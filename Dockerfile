FROM ubuntu:15.04

RUN apt-get update \
  && apt-get -y --force-yes install git python

RUN git clone https://github.com/met-office-lab/ogc-web-services ogc
RUN cd ogc && python setup.py

RUN git clone https://github.com/met-office-lab/beta-data-services bds
RUN cd bds && python setup.py

ADD [^.]* ./
