FROM python:3.8-slim

RUN mkdir /opt/crypto-monitor
COPY . /opt/crypto-monitor

RUN /usr/local/bin/python3 -m pip install --upgrade pip
RUN cd /opt/crypto-monitor/src && pip3 install --user -r requirements.txt

WORKDIR /opt/crypto-monitor

ENTRYPOINT ["/usr/local/bin/python", "./src/monitor.py"]