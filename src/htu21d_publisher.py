#!/usr/bin/env python
#
#  Copyright 2018, CRS4 - Center for Advanced Studies, Research and Development in Sardinia
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import os
import sys
import json
import time
import shutil
import signal
import socket
import logging
import influxdb
import argparse
import datetime
import platform
import configparser
import paho.mqtt.publish as publish

import Adafruit_HTU21D.HTU21D as HTU21D
import continuous_scheduler
import housekeeping

MQTT_HOST = "localhost"         # MQTT Broker address
MQTT_PORT = 1883                # MQTT Broker port
INFLUXDB_HOST = "localhost"     # INFLUXDB address
INFLUXDB_PORT = 8086            # INFLUXDB port
GPS_LOCATION = "0.0,0.0"        # DEFAULT location

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


def htu21d_task(userdata):
    v_logger     = userdata['LOGGER']
    v_mqtt_topic = userdata['MQTT_TOPIC'] + '.HTU21D'
    v_mqtt_host  = userdata['MQTT_HOST']
    v_mqtt_port  = userdata['MQTT_PORT']
    v_i2c_bus    = userdata['I2C_BUS']

    v_influxdb_host = userdata['INFLUXDB_HOST']
    v_influxdb_port = userdata['INFLUXDB_PORT']
    v_influxdb_username = userdata['INFLUXDB_USER']
    v_influxdb_password = userdata['INFLUXDB_PASS']
    v_influxdb_database = userdata['INFLUXDB_DB']

    m = dict()

    t_now = datetime.datetime.now().timestamp()
    v_timestamp = int(t_now)

    m['dateObserved'] = datetime.datetime.fromtimestamp(v_timestamp,
                    tz=datetime.timezone.utc).isoformat()
    m['timestamp'] = v_timestamp
    m['latitude']  = userdata['LATITUDE']
    m['longitude'] = userdata['LONGITUDE']

    htu21d = HTU21D.HTU21D(busnum=v_i2c_bus)

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
                username=v_influxdb_username,
                password=v_influxdb_password,
                database=v_influxdb_database
            )

            _client.write_points(_json_data, time_precision='s')
            v_logger.debug("Insert data into InfluxDB: {:s}".format(str(_json_data)))
        except Exception as ex:
            v_logger.error(ex)
        finally:
            _client.close()

    try:
        v_payload = json.dumps(m)
        v_logger.debug("Message topic:\'{:s}\', broker:\'{:s}:{:d}\', "
            "message:\'{:s}\'".format(v_mqtt_topic, v_mqtt_host, v_mqtt_port, v_payload))
        publish.single(v_mqtt_topic, v_payload, hostname=v_mqtt_host,
            port=v_mqtt_port)
    except socket.error:
        pass

def configuration_parser(p_args=None):
    pre_parser = argparse.ArgumentParser(add_help=False)

    pre_parser.add_argument('-c', '--config-file', dest='config_file', action='store',
        type=str, metavar='FILE',
        help='specify the config file')

    args, remaining_args = pre_parser.parse_known_args(p_args)

    v_general_config_defaults = {
        'mqtt_host'     : MQTT_HOST,
        'mqtt_port'     : MQTT_PORT,
        'logging_level' : logging.INFO,
        'influxdb_host' : INFLUXDB_HOST,
        'influxdb_port' : INFLUXDB_PORT,
        'gps_location'  : GPS_LOCATION,
        }

    v_specific_config_defaults = {
        'interval'      : ACQUISITION_INTERVAL,
        'i2c_bus'       : I2C_BUS_NUM
        }

    v_config_section_defaults = {
        'GENERAL': v_general_config_defaults,
        APPLICATION_NAME: v_specific_config_defaults
        }

    # Default config values initialization
    v_config_defaults = {}
    v_config_defaults.update(v_general_config_defaults)
    v_config_defaults.update(v_specific_config_defaults)

    if args.config_file:
        _config = configparser.ConfigParser()
        _config.read_dict(v_config_section_defaults)
        _config.read(args.config_file)

        # Filter out GENERAL options not listed in v_general_config_defaults
        _general_defaults = {_key: _config.get('GENERAL', _key) for _key in
                _config.options('GENERAL') if _key in
                v_general_config_defaults}

        # Updates the defaults dictionary with general and application specific
        # options
        v_config_defaults.update(_general_defaults)
        v_config_defaults.update(_config.items(APPLICATION_NAME))

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
    parser.add_argument('--i2c-bus', dest='i2c_bus', action='store',
        type=int,
        help='I2C bus number to which the sensor is attached '
        '(default: {})'.format(I2C_BUS_NUM))
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
    parser.add_argument('--gps-location', dest='gps_location', action='store',
        type=str,
        help='GPS coordinates of the sensor as latitude,longitude (default: {})'.format(GPS_LOCATION))

    args = parser.parse_args(remaining_args)
    return args


def main():
    # Initializes the default logger
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    logger = logging.getLogger(APPLICATION_NAME)

    # Checks the Python Interpeter version
    if (sys.version_info < (3, 0)):
        ###TODO: Print error message here
        sys.exit(-1)

    args = configuration_parser()

    logger.setLevel(args.logging_level)

    signal.signal(signal.SIGINT, signal_handler)

    logger.info("Starting {:s}".format(APPLICATION_NAME))
    logger.debug(vars(args))

    v_mqtt_topic = 'DeviceStatus/' + 'EDGE'
    v_latitude, v_longitude = map(float, args.gps_location.split(','))

    v_influxdb_host = args.influxdb_host
    v_influxdb_port = args.influxdb_port

    # TODO: FROM CONFIG?
    v_influxdb_database = 'edgedevicehandler'

    #v_influxdb_username = args.influxdb_username
    #v_influxdb_password = args.influxdb_password
    v_influxdb_username = 'root'
    v_influxdb_password = 'root'

    _client = influxdb.InfluxDBClient(
        host=v_influxdb_host,
        port=v_influxdb_port,
        username=v_influxdb_username,
        password=v_influxdb_password,
        database=v_influxdb_database
    )

    _dbs = _client.get_list_database()
    if v_influxdb_database not in [_d['name'] for _d in _dbs]:
        logger.info("InfluxDB database '{:s}' not found. Creating a new one.".format(v_influxdb_database))
        _client.create_database(v_influxdb_database)

    _client.close()

    _userdata = {
        'LOGGER'     : logger,
        'LATITUDE'   : v_latitude,
        'LONGITUDE'  : v_longitude,
        'MQTT_TOPIC' : v_mqtt_topic,
        'MQTT_HOST'  : args.mqtt_host,
        'MQTT_PORT'  : args.mqtt_port,
        'I2C_BUS'    : args.i2c-bus,

        'INFLUXDB_HOST': v_influxdb_host,
        'INFLUXDB_PORT': v_influxdb_port,
        'INFLUXDB_USER': v_influxdb_username,
        'INFLUXDB_PASS': v_influxdb_password,
        'INFLUXDB_DB'  : v_influxdb_database
    }

    _main_scheduler = continuous_scheduler.MainScheduler()
    _main_scheduler.add_task(housekeeping.acquire, 0, 20, 0, _userdata)
    _main_scheduler.add_task(htu21d_task, 0, 10, 0, _userdata)
    _main_scheduler.start()


if __name__ == "__main__":
    main()

# vim:ts=4:expandtab
