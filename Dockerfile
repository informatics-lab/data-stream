FROM ubuntu:15.04

RUN apt-get update \
  && apt-get -y --force-yes install git python python-setuptools python-pip

RUN git clone https://github.com/met-office-lab/ogc-web-services ogc
RUN cd ogc && python setup.py install

RUN git clone https://github.com/met-office-lab/beta-data-services bds
RUN cd bds && python setup.py install

ADD ./requirements.txt ./requirements.txt
ADD ./datastream/__init__.py ./datastream/__init__.py
ADD ./datastream/data_requests.txt ./datastream/data_requests.txt
ADD ./datastream/thredds_data_stream.py ./datastream/thredds_data_stream.py

RUN pip install -r requirements.txt

CMD python ./datastream/thredds_data_stream.py