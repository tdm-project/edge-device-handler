#!/usr/bin/env python
#
#  Copyright 2018, CRS4 - Center for Advanced Studies, Research and Development
#  in Sardinia
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

"""
This module tests:
    * that the GENERAL options defined for all the TDM modules are defined and
    work as expected;
    * the specific section overrides the GENERAL one;
    * the specific options work as expected;
    * the command line options override the configuration file.
"""

import os
import logging
import unittest

from unittest.mock import Mock
from htu21d_publisher import configuration_parser


class TestCommandLineParser(unittest.TestCase):
    """"
    Tests if the command line options override the settings in the
    configuration file.
    """

    def setUp(self):
        self._test_options = Mock()
        self._test_options.mqtt_host = 'mosquitto'
        self._test_options.mqtt_port = 8883
        self._test_options.influxdb_host = 'influxdb'
        self._test_options.influxdb_port = 8089
        self._test_options.logging_level = 10
        self._test_options.gps_location = '1.2345678,1.2345678'
        self._test_options.interval = 10
        self._test_options.i2c_bus = 5

        self._test_configuration = Mock()
        self._test_configuration.mqtt_host = 'mqtt_from_file'
        self._test_configuration.mqtt_port = 1024
        self._test_configuration.influxdb_host = 'influx_from_file'
        self._test_configuration.influxdb_port = 1025
        self._test_configuration.logging_level = 50
        self._test_configuration.gps_location = '3.6925814,4.8260482'
        self._test_configuration.interval = 120
        self._test_configuration.i2c_bus = 10

        self._config_file = '/tmp/config.ini'

        _f = open(self._config_file, "w")
        _f.write("[HTU21D_publisher]\n")
        _f.write("mqtt_host = {}\n".format(self._test_configuration.mqtt_host))
        _f.write("mqtt_port = {}\n".format(self._test_configuration.mqtt_port))
        _f.write("influxdb_host = {}\n".format(
            self._test_configuration.influxdb_host))
        _f.write("influxdb_port = {}\n".format(
            self._test_configuration.influxdb_port))
        _f.write("logging_level = {}\n".format(
            self._test_configuration.logging_level))
        _f.write("gps_location  = {}\n".format(
            self._test_configuration.gps_location))
        _f.write("interval  = {}\n".format(
            self._test_configuration.interval))
        _f.write("i2c_bus  = {}\n".format(
            self._test_configuration.i2c_bus))
        _f.close()

    def test_command_line_long(self):
        """"
        Tests if the command line options are parsed.
        """
        _cmd_line = []

        _cmd_line.extend(['--config-file', None])
        _cmd_line.extend(
            ['--mqtt-host', str(self._test_options.mqtt_host)])
        _cmd_line.extend(
            ['--mqtt-port', str(self._test_options.mqtt_port)])
        _cmd_line.extend(
            ['--influxdb-host', str(self._test_options.influxdb_host)])
        _cmd_line.extend(
            ['--influxdb-port', str(self._test_options.influxdb_port)])
        _cmd_line.extend(
            ['--logging-level', str(self._test_options.logging_level)])
        _cmd_line.extend(
            ['--gps-location', str(self._test_options.gps_location)])
        _cmd_line.extend(
            ['--interval', str(self._test_options.interval)])
        _cmd_line.extend(
            ['--i2c-bus', str(self._test_options.i2c_bus)])

        _args = configuration_parser(_cmd_line)

        self.assertEqual(
            self._test_options.mqtt_host, _args.mqtt_host)
        self.assertEqual(
            self._test_options.mqtt_port, _args.mqtt_port)
        self.assertEqual(
            self._test_options.logging_level, _args.logging_level)
        self.assertEqual(
            self._test_options.influxdb_host, _args.influxdb_host)
        self.assertEqual(
            self._test_options.influxdb_port, _args.influxdb_port)
        self.assertEqual(
            self._test_options.gps_location, _args.gps_location)
        self.assertEqual(
            self._test_options.interval, _args.interval)
        self.assertEqual(
            self._test_options.i2c_bus, _args.i2c_bus)

    def test_command_line_long_override(self):
        """"
        Tests if the command line options override the settings in the
        configuration file (long options).
        """
        _cmd_line = []

        _cmd_line.extend(
            ['--config-file', str(self._config_file)])
        _cmd_line.extend(
            ['--mqtt-host', str(self._test_options.mqtt_host)])
        _cmd_line.extend(
            ['--mqtt-port', str(self._test_options.mqtt_port)])
        _cmd_line.extend(
            ['--influxdb-host', str(self._test_options.influxdb_host)])
        _cmd_line.extend(
            ['--influxdb-port', str(self._test_options.influxdb_port)])
        _cmd_line.extend(
            ['--logging-level', str(self._test_options.logging_level)])
        _cmd_line.extend(
            ['--gps-location', str(self._test_options.gps_location)])
        _cmd_line.extend(
            ['--interval', str(self._test_options.interval)])
        _cmd_line.extend(
            ['--i2c-bus', str(self._test_options.i2c_bus)])

        _args = configuration_parser(_cmd_line)

        self.assertEqual(
            self._test_options.mqtt_host, _args.mqtt_host)
        self.assertEqual(
            self._test_options.mqtt_port, _args.mqtt_port)
        self.assertEqual(
            self._test_options.logging_level, _args.logging_level)
        self.assertEqual(
            self._test_options.influxdb_host, _args.influxdb_host)
        self.assertEqual(
            self._test_options.influxdb_port, _args.influxdb_port)
        self.assertEqual(
            self._test_options.gps_location, _args.gps_location)
        self.assertEqual(
            self._test_options.interval, _args.interval)
        self.assertEqual(
            self._test_options.i2c_bus, _args.i2c_bus)

    def test_command_line_long_partial_override(self):
        """"
        Tests if the command line options override the settings in the
        configuration file (long options).
        """
        _cmd_line = []

        _cmd_line.extend(
            ['--config-file', str(self._config_file)])
        _cmd_line.extend(
            ['--mqtt-host', str(self._test_options.mqtt_host)])
        _cmd_line.extend(
            ['--influxdb-host', str(self._test_options.influxdb_host)])
        _cmd_line.extend(
            ['--logging-level', str(self._test_options.logging_level)])
        _cmd_line.extend(
            ['--gps-location', str(self._test_options.gps_location)])
        _cmd_line.extend(
            ['--interval', str(self._test_options.interval)])

        _args = configuration_parser(_cmd_line)

        self.assertEqual(
            self._test_options.mqtt_host, _args.mqtt_host)
        self.assertEqual(
            self._test_configuration.mqtt_port, _args.mqtt_port)
        self.assertEqual(
            self._test_options.logging_level, _args.logging_level)
        self.assertEqual(
            self._test_options.influxdb_host, _args.influxdb_host)
        self.assertEqual(
            self._test_configuration.influxdb_port, _args.influxdb_port)
        self.assertEqual(
            self._test_options.gps_location, _args.gps_location)
        self.assertEqual(
            self._test_options.interval, _args.interval)
        self.assertEqual(
            self._test_configuration.i2c_bus, _args.i2c_bus)

    def tearDown(self):
        os.remove(self._config_file)


class TestConfigFileParser(unittest.TestCase):
    """"
    Checks if the GENERAL section of the configuration file is read and parsed.
    """

    def setUp(self):
        self._test_mqtt_host = 'mosquitto'
        self._test_mqtt_port = 8883
        self._test_influxdb_host = 'influxdb'
        self._test_influxdb_port = 8089
        self._test_logging_level = 10
        self._test_gps_location = '1.2345678,1.2345678'

        self._config_file = '/tmp/config.ini'
        _f = open(self._config_file, "w")
        _f.write("[GENERAL]\n")
        _f.write("mqtt_host = {}\n".format(self._test_mqtt_host))
        _f.write("mqtt_port = {}\n".format(self._test_mqtt_port))
        _f.write("influxdb_host = {}\n".format(self._test_influxdb_host))
        _f.write("influxdb_port = {}\n".format(self._test_influxdb_port))
        _f.write("logging_level = {}\n".format(self._test_logging_level))
        _f.write("gps_location  = {}\n".format(self._test_gps_location))
        _f.close()

    def test_general_options(self):
        """
        Tests the parsing of the options in the GENERAL section.
        """

        _cmd_line = ['-c', self._config_file]
        _args = configuration_parser(_cmd_line)

        self.assertEqual(self._test_mqtt_host, _args.mqtt_host)
        self.assertEqual(self._test_mqtt_port, _args.mqtt_port)
        self.assertEqual(self._test_logging_level, _args.logging_level)
        self.assertEqual(self._test_influxdb_host, _args.influxdb_host)
        self.assertEqual(self._test_influxdb_port, _args.influxdb_port)
        self.assertEqual(self._test_gps_location, _args.gps_location)

    def test_general_override_options(self):
        """
        Tests if the options in the GENERAL section are overridden by the same
        options in the specific section.
        """
        _test_override_mqtt_host = 'mosquitto'
        _test_override_mqtt_port = 8883
        _test_override_influxdb_host = 'influxdb'
        _test_override_influxdb_port = 8089
        _test_override_logging_level = 10
        _test_override_gps_location = '1.2345678,1.2345678'

        _config_specific_override_file = '/tmp/override_config.ini'

        _f = open(_config_specific_override_file, "w")
        _f.write("[GENERAL]\n")
        _f.write("mqtt_host = {}\n".format(self._test_mqtt_host))
        _f.write("mqtt_port = {}\n".format(self._test_mqtt_port))
        _f.write("influxdb_host = {}\n".format(self._test_influxdb_host))
        _f.write("influxdb_port = {}\n".format(self._test_influxdb_port))
        _f.write("logging_level = {}\n".format(self._test_logging_level))
        _f.write("gps_location  = {}\n".format(self._test_gps_location))
        _f.write("[HTU21D_publisher]\n")
        _f.write("mqtt_host = {}\n".format(_test_override_mqtt_host))
        _f.write("mqtt_port = {}\n".format(_test_override_mqtt_port))
        _f.write("influxdb_host = {}\n".format(_test_override_influxdb_host))
        _f.write("influxdb_port = {}\n".format(_test_override_influxdb_port))
        _f.write("logging_level = {}\n".format(_test_override_logging_level))
        _f.write("gps_location  = {}\n".format(_test_override_gps_location))
        _f.close()

        _cmd_line = ['-c', _config_specific_override_file]
        _args = configuration_parser(_cmd_line)

        self.assertEqual(_test_override_mqtt_host, _args.mqtt_host)
        self.assertEqual(_test_override_mqtt_port, _args.mqtt_port)
        self.assertEqual(_test_override_logging_level, _args.logging_level)
        self.assertEqual(_test_override_influxdb_host, _args.influxdb_host)
        self.assertEqual(_test_override_influxdb_port, _args.influxdb_port)
        self.assertEqual(_test_override_gps_location, _args.gps_location)

        os.remove(_config_specific_override_file)

    def tearDown(self):
        os.remove(self._config_file)


class TestGeneralOptions(unittest.TestCase):
    """
    Checks if the GENERAL section options are present in the parser and their
    default values are defined
    """

    def setUp(self):
        self._default_mqtt_host = 'localhost'
        self._default_mqtt_port = 1883
        self._default_influxdb_host = 'localhost'
        self._default_influxdb_port = 8086
        self._default_logging_level = logging.INFO
        self._default_gps_location = '0.0,0.0'

    def test_general_arguments(self):
        """
        Checks the presence of the GENERAL section in the parser.
        """
        _args = configuration_parser()

        self.assertIn('mqtt_host', _args)
        self.assertIn('mqtt_port', _args)
        self.assertIn('logging_level', _args)
        self.assertIn('influxdb_host', _args)
        self.assertIn('influxdb_port', _args)
        self.assertIn('gps_location', _args)

    def test_general_default(self):
        """
        Checks the defaults of the GENERAL section in the parser.
        """
        _args = configuration_parser()

        self.assertEqual(self._default_mqtt_host, _args.mqtt_host)
        self.assertEqual(self._default_mqtt_port, _args.mqtt_port)
        self.assertEqual(self._default_logging_level, _args.logging_level)
        self.assertEqual(self._default_influxdb_host, _args.influxdb_host)
        self.assertEqual(self._default_influxdb_port, _args.influxdb_port)
        self.assertEqual(self._default_gps_location, _args.gps_location)


class TestSpecificOptions(unittest.TestCase):
    """
    Checks if the specific options are present in the parser and their
    default values are defined
    """

    def setUp(self):
        self._default_interval = 60
        self._default_i2c_bus = 1

        self._test_interval = 10
        self._test_i2c_bus = 5

        self._config_file = '/tmp/config.ini'
        _f = open(self._config_file, "w")
        _f.write("[HTU21D_publisher]\n")
        _f.write("interval = {}\n".format(self._test_interval))
        _f.write("i2c_bus = {}\n".format(self._test_i2c_bus))
        _f.close()

    def test_specific_arguments(self):
        """
        Checks the presence of the specific options in the parser.
        """
        _args = configuration_parser()

        self.assertIn('interval', _args)
        self.assertIn('i2c_bus', _args)

    def test_specific_default(self):
        """
        Checks the default values of the specific options in the parser.
        """
        _args = configuration_parser()

        self.assertEqual(self._default_interval, _args.interval)
        self.assertEqual(self._default_i2c_bus, _args.i2c_bus)

    def test_specific_options(self):
        """
        Tests the parsing of the options in the specific section.
        """
        _cmd_line = ['-c', self._config_file]
        _args = configuration_parser(_cmd_line)

        self.assertEqual(self._test_interval, _args.interval)
        self.assertEqual(self._test_i2c_bus, _args.i2c_bus)

    def tearDown(self):
        os.remove(self._config_file)


if __name__ == '__main__':
    unittest.main()
