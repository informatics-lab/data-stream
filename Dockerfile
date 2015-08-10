FROM ubuntu:15.04

RUN apt-get update \
  && apt-get -y --force-yes install git python python-setuptools python-pip

ADD ./thredds_data_stream.py ./thredds_data_stream.py

RUN pip install -r requirements.txt

CMD python ./thredds_data_stream.py
