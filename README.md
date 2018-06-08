Build docker image with:
```
docker build . -f docker/Dockerfile -t tdm/htu21d_publisher
```

Config file example:

```
[HTU21D_publisher]
mqtt_host = mosquitto
mqtt_port = 1883
interval=10
logging_level = 0
```
