Build docker image with:
```
docker build . -f docker/Dockerfile -t tdm/htu21d_publisher
```


## Configurations
Settings are retrieved from both configuration file and command line.
Values are applied in the following order, the last overwriting the previous:

1. configuration file section '***GENERAL***' for the common options (logging, local MQTT broker...);
2. configuration file section '***HTU21D\_publisher***' for both common and specific options;
3. command line options.

### Configuration file
* **mqtt\_host**

   hostname or address of the local broker (default: *localhost*)
* **mqtt\_port**

   port of the local broker (default: *1883*)
* **logging\_level**

   threshold level for log messages (default: *20*)
* **influxdb\_host**

   hostname or address of the influx database (default: *localhost*)
* **influxdb\_port**

   port of the influx database (default: *8086*)
* **gps\_location**

   GPS coordinates of the sensor as latitude,longitude (default: *0.0,0.0*)
* **interval**

   interval in seconds for data acquisition and publication (default: *60 secs*)
* **i2c\_bus**

   I2C bus number to which the sensor is attached (default: *1*)

When a settings is present both in the *GENERAL* and *application specific*  section, the application specific is applied to the specific handler.

In this example, the *logging\_level* settings is overwritten to *1* only for this handler, while other handlers use *0* from the section *GENERAL*:

```ini
[GENERAL]
mqtt_host = mosquitto
mqtt_port = 1883
influxdb_host = influxdb
influxdb_port = 8086
gps_location=0.0,0.0
logging_level = 0

[HTU21D_publisher]
interval=10
logging_level = 1
i2c_bus = 1
```

### Command line
*  **-h, --help**

   show this help message and exit
*  **-c FILE, --config-file FILE**

   specify the config file
*  **-l LOGGING\_LEVEL, --logging-level LOGGING\_LEVEL**

   threshold level for log messages (default: *20*)
*  **--mqtt-host MQTT\_HOST**

   hostname or address of the local broker (default: *localhost*)
*  **--mqtt-port MQTT\_PORT**

   port of the local broker (default: *1883*)
*  **--i2c-bus I2C\_BUS**

   I2C bus number to which the sensor is attached (default: *1*)
*  **--interval INTERVAL**

   interval in seconds for data acquisition and publication (default: *60 secs*)
*  **--influxdb-host INFLUXDB\_HOST**

   hostname or address of the influx database (default: *localhost*)
*  **--influxdb-port INFLUXDB\_PORT**

   port of the influx database (default: *8086*)
*  **--gps-location GPS\_LOCATION**

   GPS coordinates of the sensor as latitude,longitude (default: *0.0,0.0*)
