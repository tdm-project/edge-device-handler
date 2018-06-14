#!/usr/bin/env python

import sys
import json
import time
import signal
import socket
import logging
import influxdb
import argparse
import datetime
import configparser
import paho.mqtt.publish as publish

import Adafruit_HTU21D.HTU21D as HTU21D


MQTT_HOST = "localhost"         # MQTT Broker address
MQTT_PORT = 1883                # MQTT Broker port
INFLUXDB_HOST = "localhost"     # INFLUXDB address
INFLUXDB_PORT = 8086            # INFLUXDB port

I2C_BUS_NUM = 1             # Default I2C Bus Number (RPi2/3)
ACQUISITION_INTERVAL = 60   # Seconds between two acquisitions and transmissions


APPLICATION_NAME = 'HTU21D_publisher'


PROVIDES = [                # What measures we are providing
    'temperature',
    'humidity',
    'dewpoint'
]


def signal_handler(sig, frame):
    sys.exit(0)


def main():
    # Initializes the default logger
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    logger = logging.getLogger(APPLICATION_NAME)

    # Checks the Python Interpeter version
    if (sys.version_info < (3, 0)):
        ###TODO: Print error message here
        sys.exit(-1)

    pre_parser = argparse.ArgumentParser(add_help=False)

    pre_parser.add_argument('-c', '--config-file', dest='config_file', action='store',
        type=str, metavar='FILE',
        help='specify the config file')

    args, remaining_args = pre_parser.parse_known_args()

    v_config_defaults = {
        'mqtt_host'     : MQTT_HOST,
        'mqtt_port'     : MQTT_PORT,
        'logging_level' : logging.INFO,
        'influxdb_host' : INFLUXDB_HOST,
        'influxdb_port' : INFLUXDB_PORT,

        'interval'      : ACQUISITION_INTERVAL,
        'i2c_bus'       : I2C_BUS_NUM
        }

    v_config_section_defaults = {
        APPLICATION_NAME: v_config_defaults
        }

    if args.config_file:
        v_config = configparser.ConfigParser()
        v_config.read_dict(v_config_section_defaults)
        v_config.read(args.config_file)

        v_config_defaults = dict(v_config.items(APPLICATION_NAME))

    parser = argparse.ArgumentParser(parents=[pre_parser],
            description='Acquire data from HTU21D temperature/humidity sensor and publish them to a local MQTT broker.',
            formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.set_defaults(**v_config_defaults)

    parser.add_argument('-l', '--logging-level', dest='logging_level', action='store',
        type=int,
        help='threshold level for log messages (default: {})'.format(logging.INFO))
    parser.add_argument('--mqtt-host', dest='mqtt_host', action='store',
        type=str,
        help='hostname or address of the local broker (default: {})'
            .format(MQTT_HOST))
    parser.add_argument('--mqtt-port', dest='mqtt_port', action='store',
        type=int,
        help='port of the local broker (default: {})'.format(MQTT_PORT))
    parser.add_argument('--i2c_bus', dest='i2c_bus', action='store',
        type=int,
        help='I2C bus number to which the sensor is attached '
        '(default: {} secs)'.format(I2C_BUS_NUM))
    parser.add_argument('--interval', dest='interval', action='store',
        type=int,
        help='interval in seconds for data acquisition and publication '
        '(default: {} secs)'.format(ACQUISITION_INTERVAL))
    parser.add_argument('--influxdb-host', dest='influxdb_host', action='store',
        type=str,
        help='hostname or address of the influx database (default: {})'
            .format(INFLUXDB_HOST))
    parser.add_argument('--influxdb-port', dest='influxdb_port', action='store',
        type=int,
        help='port of the influx database (default: {})'.format(INFLUXDB_PORT))

    args = parser.parse_args()

    logger.setLevel(args.logging_level)

    signal.signal(signal.SIGINT, signal_handler)

    logger.info("Starting {:s}".format(APPLICATION_NAME))
    logger.debug(vars(args))

    v_mqtt_topic = 'Device/' + 'EDGE.HTU21D'

    htu21d = HTU21D.HTU21D(busnum=args.i2c_bus)

    # TODO: FROM CONFIG?
    v_influx_db     = 'edgedevicehandler'

    #v_influxdb_username = args.influxdb_username
    #v_influxdb_password = args.influxdb_password
    v_influxdb_username = 'root'
    v_influxdb_password = 'root'

    v_influxdb_host = args.influxdb_host
    v_influxdb_port = args.influxdb_port

    _client = influxdb.InfluxDBClient(
        host=v_influxdb_host,
        port=v_influxdb_port,
        username=v_influxdb_username,
        password=v_influxdb_password,
        database=v_influx_db
    )

    _dbs = _client.get_list_database()
    if v_influx_db not in [_d['name'] for _d in _dbs]:
        logger.info("InfluxDB database '{:s}' not found. Creating a new one.".format(v_influx_db))
        _client.create_database(v_influx_db)

    _client.close()

    while True:
        m = dict()

        t_now = datetime.datetime.now().timestamp()
        v_timestamp = int(t_now)

        m['timestamp'] = v_timestamp

        try:
            htu21d.reset()

            m["temperature"] = htu21d.read_temperature()
            m["humidity"]    = htu21d.read_humidity()
            m["dewpoint"]    = htu21d.read_dewpoint()

            _json_data = [ {
                "measurement": "sensors",
                "tags": {
                    "sensor": "htu21d",
                },
                "time": m['timestamp'],
                "fields": {
                    "temperature": m['temperature'],
                    "humidity":    m['humidity'],
                    "dewpoint":    m['dewpoint']
                }
            } ]

        except IOError as iex:
            m["temperature"] = None
            m["humidity"]    = None
            m["dewpoint"]    = None

            _json_data = None

        if _json_data is not None:
            try:
                _client = influxdb.InfluxDBClient(
                    host=v_influxdb_host,
                    port=v_influxdb_port,
                    username='root',
                    password='root',
                    database=v_influx_db
                )

                _client.write_points(_json_data, time_precision='s')
                logger.debug("Insert data into InfluxDB: {:s}".format(str(_json_data)))
            except Exception as ex:
                logger.error(ex)
            finally:
                _client.close()

        try:
            v_payload = json.dumps(m)
            logger.debug("Message topic:\'{:s}\', broker:\'{:s}:{:d}\', "
                "message:\'{:s}\'".format(v_mqtt_topic, args.mqtt_host, args.mqtt_port, v_payload))
            publish.single(v_mqtt_topic, v_payload, hostname=args.mqtt_host,
                port=args.mqtt_port)
        except socket.error:
            pass

        time.sleep(args.interval)


if __name__ == "__main__":
    main()

# vim:ts=4:expandtab
