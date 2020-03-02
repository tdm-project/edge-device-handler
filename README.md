# TDM Edge Dispatcher
In [TDM Edge Gateway Reference Architecture](http://www.tdm-project.it/en/) the Edge Gateway can have sensors directly attached to its connectors. Depending on the type of interface or bus to which they are connected, a different micro-service takes care of establishing the connection, configuring the sensors on that interface and polling them periodically. For the sensor used in this reference design, the HTU21D temperature and humidity sensor, the handler is called ***Edge Device Handler*** (*HTU21D Publisher* is the legacy name and will be changed in the future). 

This handler opens the interface on the I2C bus on which the sensor operates and, at time interval set in the configuration file or command line, pools the sensor and sends to the local MQTT broker the message with the parameters detected, in this case temperature, humidity and the dew point calculated from the first two. 

Other data sent are internal housekeeping data like, kernel version, memory in use, current cpu load and others. See '***Data collected***' section below.

## Configurations
Settings are retrieved from both configuration file and command line.
Values are applied in the following order, the last overwriting the previous:

1. configuration file section '***GENERAL***' for the common options (logging, local MQTT broker...);
2. configuration file section '***HTU21D\_publisher***' for both common and specific options;
3. command line options.

### Configuration file

###  The options *mqtt\_host* and *mqtt\_port* now are deprecated and no longer recognized. *mqtt\_local\_host* and *mqtt\_local\_port* must be used instead.

* **mqtt\_local\_host**

	hostname or address of the local broker (default: *localhost*) 

* **mqtt\_local\_port**

	port of the local broker (default: *1883*)

* **logging\_level**

   threshold level for log messages (default: *20*)
* **influxdb\_host**

   hostname or address of the influx database (default: *localhost*)
* **influxdb\_port**

   port of the influx database (default: *8086*)
* **gps\_location**

   GPS coordinates of the sensor as latitude,longitude (default: *0.0,0.0*)
* **htu\_interval**

   interval in seconds for HTU21D sensor data acquisition and publication (default: *60 secs*)
* **hkp\_interval**

   interval in seconds for Housekeeping data acquisition and publication (default: *60 secs*)
* **i2c\_bus**

   I2C bus number to which the sensor is attached (default: *1*)

When a settings is present both in the *GENERAL* and *application specific*  section, the application specific is applied to the specific handler.

#### Options accepted in GENERAL section
* **mqtt\_local\_host**
* **mqtt\_local\_port**
* **influxdb\_host**
* **influxdb\_port**
* **logging\_level**
* **gps\_location**

In this example, the *logging\_level* settings is overwritten to *1* only for this handler, while other handlers use *0* from the section *GENERAL*:

```ini
[GENERAL]
mqtt_local_host = mosquitto
mqtt_local_port = 1883
influxdb_host = influxdb
influxdb_port = 8086
gps_location=0.0,0.0
logging_level = 0

[HTU21D_publisher]
htu_interval=60
hkp_interval=3600
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
*  **--htu-interval INTERVAL**

   interval in seconds for HTU21D sensor data acquisition and publication (default: *60 secs*)
* **--hkp-interval INTERVAL**

   interval in seconds for Housekeeping data acquisition and publication (default: *60 secs*)
*  **--influxdb-host INFLUXDB\_HOST**

   hostname or address of the influx database (default: *localhost*)
*  **--influxdb-port INFLUXDB\_PORT**

   port of the influx database (default: *8086*)
*  **--gps-location GPS\_LOCATION**

   GPS coordinates of the sensor as latitude,longitude (default: *0.0,0.0*)

## Data Collected
Data collected by the **Edge Device Handler** are sent with two MQTT messages to the TDM Cloud:

### HTU21 Message
* **dateObserved** measurement date in ISO format;
* **timestamp** measurement date as Unix Epoch;
* **latitude** from configuration file/command line;
* **longitude** from configuration file/command line;
* **temperature** from HTU21D sensor (also stored in the internal Influx DB);
* **humidity** from HTU21D sensor (also stored in the internal Influx DB);
* **dewpoint** computed from data HTU21D sensor (also stored in the internal Influx DB).

### HOUSEKEEPING Message
* **dateObserved** measurement date in ISO format;
* **timestamp** measurement date as Unix Epoch;
* **latitude** from configuration file/command line;
* **longitude** from configuration file/command line;
* **lastBoot** date of the last boot;
* **operatingSystem** Operating System (*Linux*);
* **kernelRelease** release of the kernel;
* **kernelVersion** build of the current kernel;
* **systemArchitecture** CPU architecture;
* **cpuCount** total CPU number;
* **diskTotal** total DISK (SD) space in MB;
* **diskFree** free DISK (SD) space available in MB;
* **memoryTotal** total RAM memory in MB;
* **memoryFree** free RAM memory available in MB
* **swapTotal** total Swap space in MB;
* **swapFree** free Swap memory available in MB.
