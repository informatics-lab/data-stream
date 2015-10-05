FROM quay.io/informaticslab/iris

RUN apt-get update \
  && apt-get -y --force-yes install git python python-setuptools python-pip

ADD ./thredds_data_stream.py ./thredds_data_stream.py
ADD ./requirements.txt ./requirements.txt

RUN git clone https://github.com/met-office-lab/cloud-processing-config.git config

RUN pip install -r requirements.txt

CMD python ./thredds_data_stream.py
