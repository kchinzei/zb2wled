# zb2wled

Translate Zigbee MQTT to [wled](https://kno.wled.ge) MQTT.
Support RGB and white with color temperature.

### required arguments
- **-u user, --username user**
  username for MQTT host to publish
- **-p pwd, --password pwd**
  password for MQTT user

### optional arguments:
- **-h, --help**            show this help message and exit
- **-H host, --host host**  MQTT host (default: 192.168.0.201)
- **-P port, --port port**  MQTT port (default: 1883)

## What it is for?

This mini project is to control [WLED](https://kno.wled.ge) bulb from
a Zigbee switch [IKEA E2002 'STYRBAR'](https://www.ikea.com/jp/en/p/styrbar-remote-control-smart-white-10488364/).

## Dependency

- Python 3.9 or later
- [paho MQTT client](https://pypi.org/project/paho-mqtt/) `pip3 install paho-mqtt`

