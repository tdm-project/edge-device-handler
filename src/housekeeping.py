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

import os
import json
import shutil
import socket
import platform
import datetime
import paho.mqtt.publish as publish


def memoryTotal():
    """
    Retrieves total system memory from /proc/meminfo in MB
    """
    meminfo = {
        _l.split()[0].rstrip(':'): int(_l.split()[1])
        for _l in open('/proc/meminfo').readlines()}
    return int(meminfo['MemTotal'] / 1024)


def memoryFree():
    """
    Retrieves free system memory from /proc/meminfo in MB
    """
    meminfo = {
        _l.split()[0].rstrip(':'): int(_l.split()[1])
        for _l in open('/proc/meminfo').readlines()}
    return int(meminfo['MemFree'] / 1024)


def swapTotal():
    meminfo = {
        _l.split()[0].rstrip(':'): int(_l.split()[1])
        for _l in open('/proc/meminfo').readlines()}
    return int(meminfo['SwapTotal'] / 1024)


def swapFree():
    meminfo = {
        _l.split()[0].rstrip(':'): int(_l.split()[1])
        for _l in open('/proc/meminfo').readlines()}
    return int(meminfo['SwapFree'] / 1024)


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


PARAMETER_FUNCTION_MAP = {
    "lastBoot" : lastBoot,
    "operatingSystem"   : platform.system,
    "kernelRelease"     : platform.release,
    "kernelVersion"     : platform.version,
    "systemArchitecture": platform.machine,
    "cpuCount" : os.cpu_count,
    "diskTotal": diskTotal,
    "diskFree" : diskFree,
    "memoryTotal": memoryTotal,
    "memoryFree ": memoryFree,
    "swapTotal"  : swapTotal,
    "swapFree"   : swapFree,

}


def acquire(userdata):
    v_logger = userdata['LOGGER']
    v_mqtt_topic = userdata['MQTT_TOPIC'] + '.HOUSEKEEPING'
    v_mqtt_host = userdata['MQTT_LOCAL_HOST']
    v_mqtt_port = userdata['MQTT_LOCAL_PORT']

    m = dict()

    t_now = datetime.datetime.now().timestamp()
    v_timestamp = int(t_now)

    m['dateObserved'] = datetime.datetime.fromtimestamp(
        v_timestamp, tz=datetime.timezone.utc).isoformat()
    m['timestamp'] = v_timestamp
    m['latitude'] = userdata['LATITUDE']
    m['longitude'] = userdata['LONGITUDE']

    for _parm in PARAMETER_FUNCTION_MAP:
        try:
            m[_parm] = PARAMETER_FUNCTION_MAP[_parm]()
        except Exception as ex:
            m[_parm] = None
            v_logger.error(ex)

    try:
        v_payload = json.dumps(m)
        v_logger.debug(
            "Message topic:\'{:s}\', broker:\'{:s}:{:d}\', message:\'{:s}\'".
            format(v_mqtt_topic, v_mqtt_host, v_mqtt_port, v_payload))
        publish.single(
            v_mqtt_topic, v_payload, hostname=v_mqtt_host,
            port=v_mqtt_port)
    except socket.error:
        pass
