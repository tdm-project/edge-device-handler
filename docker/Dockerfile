FROM alpine:latest

ENV APP_HOME=/opt/htu21d/

# Install required packages
RUN apk add --no-cache python3 git && \
	pip3 install virtualenv

RUN \
	mkdir -p ${APP_HOME} && \
	cd ${APP_HOME} && \
	virtualenv venv && \
	. venv/bin/activate && \
	pip3 install paho-mqtt influxdb

WORKDIR ${APP_HOME}

RUN . venv/bin/activate && git clone https://github.com/mgaggero/Adafruit_Python_HTU21D.git && \
	cd Adafruit_Python_HTU21D && python3 setup.py install

COPY src src

ENTRYPOINT ["src/entrypoint.sh"]

CMD [ "-c", "/opt/tdm.conf" ]
