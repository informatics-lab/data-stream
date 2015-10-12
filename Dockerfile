FROM quay.io/informaticslab/iris

RUN apt-get update \
  && apt-get -y --force-yes install git python python-setuptools python-pip

ADD ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
ADD ./timeout.py ./timeout.py

RUN git clone https://github.com/met-office-lab/cloud-processing-config.git config

ADD ./thredds_data_stream.py ./thredds_data_stream.py

CMD python ./thredds_data_stream.py
