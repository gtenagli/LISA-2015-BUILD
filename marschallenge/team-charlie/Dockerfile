FROM ubuntu:15.10
MAINTAINER Giacomo Tenaglia <Giacomo.Tenaglia@gmail.com>
RUN apt-get update && apt-get install -y python python-requests python-websocket
ADD Team-Client.py /Team-Client.py
CMD python /Team-Client.py > /Team-Client.py
