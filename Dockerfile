FROM ubuntu:15.04

RUN apt-get update \
  && apt-get -y --force-yes install git python python-setuptools

RUN git clone https://github.com/met-office-lab/ogc-web-services ogc
RUN cd ogc && python setup.py install

RUN git clone https://github.com/met-office-lab/beta-data-services bds
RUN cd bds && python setup.py install

ADD [^.]* ./
RUN python setup.py install

CMD python thredds_data_stream.py
