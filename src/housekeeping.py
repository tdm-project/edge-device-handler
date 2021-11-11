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

import influxdb
import statistics
import tcp_latency
import os
import json
import shutil
import socket
import platform
import datetime
import psutil
import subprocess as subp
import paho.mqtt.publish as publish


def memoryTotal():
    """
    Retrieves total system memory in MB
    """
    _m = psutil.virtual_memory()
    return int(_m.total / (1024 * 1024))


def memoryFree():
    """
    Retrieves free system memory in MB
    """
    _m = psutil.virtual_memory()
    return int(_m.free / (1024 * 1024))


def memoryAvailable():
    """
    Retrieves total available system memory in MB
    """
    _m = psutil.virtual_memory()
    return int(_m.available / (1024 * 1024))


def swapTotal():
    _s = psutil.swap_memory()
    return int(_s.total / (1024 * 1024))


def swapFree():
    _s = psutil.swap_memory()
    return int(_s.free / (1024 * 1024))


def lastBoot():
    _seconds = 0

    with open('/proc/uptime', 'r') as _u:
        _seconds = float(_u.readline().split()[0])

    _last_boot = datetime.datetime.now() - datetime.timedelta(seconds=_seconds)
    return _last_boot.strftime('%Y-%m-%d %H:%M:%S')


def diskTotal():
    _total, _used, _free = shutil.disk_usage('/')
    return int(_total / (1024 * 1024))


def diskFree():
    _total, _used, _free = shutil.disk_usage('/')
    return int(_free / (1024 * 1024))


def rssiSignal():
    _exec = "wpa_cli"
    _sock = "/var/run/wpa_supplicant"
    _ifac = "wlan0"
    _comd = "signal_poll"

    try:
        _r = subp.Popen([_exec, '-s', _sock, '-i', _ifac, _comd],
                        stdout=subp.PIPE, stderr=subp.PIPE)
        _std_out, _std_err = _r.communicate()
    except (OSError, ValueError):
        return None
    else:
        if _r.wait() != 0:
            return None
        else:
            _signal = [_s.split(b'=')[1] for _s in _std_out.split()
                       if _s.lower().startswith(b'rssi=')]

    return int(_signal[0])


def tcpLatency():
    _ls = tcp_latency.measure_latency(host='google.com', runs=5, timeout=2.5)
    _latency = statistics.median(_ls)
    _latency = int(_latency * 100) / 100

    return _latency


def cpuLoad():
    _l_1, _l_5, _l_15 = psutil.getloadavg()
    return _l_1


def cpuTemp():
    _temp = None

    with open('/sys/class/thermal/thermal_zone0/temp') as _tf:
        _temp = int(_tf.readline()) / 1000

    return _temp


def uptime():
    _uptime = datetime.datetime.now().timestamp() - psutil.boot_time()
    return _uptime


PARAMETER_FUNCTION_MAP = {
    "lastBoot": lastBoot,
    "operatingSystem": platform.system,
    "kernelRelease": platform.release,
    "kernelVersion": platform.version,
    "systemArchitecture": platform.machine,
    "cpuCount": os.cpu_count,
    "diskTotal": diskTotal,
    "diskFree": diskFree,
    "memoryTotal": memoryTotal,
    "memoryFree": memoryFree,
    "memoryAvailable": memoryAvailable,
    "swapTotal": swapTotal,
    "swapFree": swapFree,
    "signal": rssiSignal,
    "tcpLatency": tcpLatency,
    "cpuLoad": cpuLoad,
    "cpuTemp": cpuTemp,
    "uptime": uptime
}


TO_SEND = [
    "lastBoot",
    "operatingSystem",
    "kernelRelease",
    "kernelVersion",
    "systemArchitecture",
    "cpuCount",
    "diskTotal",
    "diskFree",
    "memoryTotal",
    "memoryFree",
    "swapTotal",
    "swapFree"
]


def acquire(userdata):
    v_logger = userdata['LOGGER']
    v_mqtt_topic = userdata['MQTT_TOPIC'] + '.HOUSEKEEPING'
    v_mqtt_host = userdata['MQTT_LOCAL_HOST']
    v_mqtt_port = userdata['MQTT_LOCAL_PORT']

    _to_save = dict()

    t_now = datetime.datetime.now().timestamp()
    v_timestamp = int(t_now)

    _to_save['dateObserved'] = datetime.datetime.fromtimestamp(
        v_timestamp, tz=datetime.timezone.utc).isoformat()
    _to_save['timestamp'] = v_timestamp
    _to_save['latitude'] = userdata['LATITUDE']
    _to_save['longitude'] = userdata['LONGITUDE']

    for _parm in PARAMETER_FUNCTION_MAP:
        try:
            _to_save[_parm] = PARAMETER_FUNCTION_MAP[_parm]()
        except Exception as ex:
            _to_save[_parm] = None
            v_logger.error(ex)

    try:
        _json_data = [{
            "measurement": "telemetry",
            # "tags": {
            #     "sensor": "htu21d",
            # },
            "time": _to_save['timestamp'],
            "fields": _to_save
        }]
        _client = influxdb.InfluxDBClient(
            host=userdata['INFLUXDB_HOST'],
            port=userdata['INFLUXDB_PORT'],
            username=userdata['INFLUXDB_USER'],
            password=userdata['INFLUXDB_PASS'],
            database=userdata['INFLUXDB_DB']
        )

        _client.write_points(_json_data, time_precision='s')
        v_logger.debug(
            "Insert data into InfluxDB: {:s}".format(str(_json_data)))
    except Exception as ex:
        v_logger.error(ex)
    finally:
        _client.close()

    _to_send = {_k: _v for _k, _v in _to_save.items() if _k in TO_SEND}

    try:
        v_payload = json.dumps(_to_send)
        v_logger.debug(
            "Message topic:\'{:s}\', broker:\'{:s}:{:d}\', message:\'{:s}\'".
            format(v_mqtt_topic, v_mqtt_host, v_mqtt_port, v_payload))
        publish.single(
            v_mqtt_topic, v_payload, hostname=v_mqtt_host,
            port=v_mqtt_port)
    except socket.error:
        pass
