FROM amazonlinux:2

RUN yum -y install python3-pip
RUN yum -y install wget
RUN yum -y install perl 
RUN yum -y install pigz
RUN yum -y install gzip 

COPY pyir/ /tmp/pyir/
COPY SetupGermlineLibrary.sh /tmp/
COPY bin/ /tmp/bin/
COPY edit_imgt_file.pl /tmp/
COPY setup.py /tmp/
COPY testing/ /tmp/testing


WORKDIR /tmp
RUN pip3 install .

RUN bash SetupGermlineLibrary.sh
