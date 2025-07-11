#!/usr/bin/env python3
#    The MIT License (MIT)
#    Copyright (c) Kiyo Chinzei (kchinzei@gmail.com)
#    Permission is hereby granted, free of charge, to any person obtaining a copy
#    of this software and associated documentation files (the "Software"), to deal
#    in the Software without restriction, including without limitation the rights
#    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#    copies of the Software, and to permit persons to whom the Software is
#    furnished to do so, subject to the following conditions:
#    The above copyright notice and this permission notice shall be included in
#    all copies or substantial portions of the Software.
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#    THE SOFTWARE.

REQUIRED_PYTHON_VERSION = (3, 9)
import json
import threading
import time
import argparse
import sys
import paho.mqtt.client as mqtt

defaultHost = '192.168.0.201'
defaultPort = 1883
kTopicsDictList = [
    {'topic_sub': 'zigbee2mqtt/SW01', 'type': 'wled', 'topic_pub': 'wled/1cc53a'},
    ]

kColorTempMin = 153
kColorTempMax = 500
kBrightnessMax = 255
kGamma = 2.2
        
# Global state
brightness = kBrightnessMax / 2  # Starting value
brightness_lock = threading.Lock()
colortemp = (kColorTempMax + kColorTempMin) / 2
colortemp_lock = threading.Lock()
running = False
direction = None
step = 5
interval = 0.1  # 100 ms step interval

def clamp(value, min_val, max_val):
    return max(min_val, min(value, max_val))

def gamma_correct(value):
    return int(((value / kBrightnessMax) ** kGamma) * kBrightnessMax)

def brightness_loop(client, topic):
    global brightness, running, direction
    while running:
        with brightness_lock:
            if direction == "up":
                brightness = clamp(brightness + step, 0, kBrightnessMax)
            elif direction == "down":
                brightness = clamp(brightness - step, 0, kBrightnessMax)
            # print(f"Brightness: {brightness}")
            client.publish(topic, brightness)
        time.sleep(interval)

def colortemp_loop(client, topic):
    global colortemp, running, direction
    while running:
        with colortemp_lock:
            if direction == "up":
                colortemp = clamp(colortemp + step, kColorTempMin, kColorTempMax)
            elif direction == "down":
                colortemp = clamp(colortemp - step, kColorTempMin, kColorTempMax)
            # print(f"Colortemp: {colortemp}")
            # client.publish(topic, colortemp)
        time.sleep(interval)

def on_message(client, userdata, msg):
    global running, direction
    payload = json.loads(msg.payload.decode(encoding='utf-8'))

    for d in kTopicsDictList:
        if d['topic_sub'] == msg.topic:
            action = payload['action']
            topic_pub = d['topic_pub']
            if action == "brightness_move_up":
                direction = "up"
                if not running:
                    running = True
                    threading.Thread(target=brightness_loop, args=(client, topic_pub), daemon=True).start()
            elif action == "brightness_move_down":
                direction = "down"
                if not running:
                    running = True
                    threading.Thread(target=brightness_loop, args=(client, topic_pub), daemon=True).start()
            elif action == "brightness_stop":
                running = False
            elif action == "on":
                running = False
                client.publish(topic_pub, brightness)
                client.publish(topic_pub, action)
            elif action == "off":
                running = False
                client.publish(topic_pub, 0)
                client.publish(topic_pub, action)
            elif action == "arrow_left_click":
                running = False
            elif action == "arrow_left_hold":
                direction = "down"
                if not running:
                    running = True
                    threading.Thread(target=colortemp_loop, args=(client, topic_pub), daemon=True).start()
            elif action == "arrow_left_release":
                running = False
            elif action == "arrow_right_click":
                running = False
            elif action == "arrow_right_hold":
                direction = "up"
                if not running:
                    running = True
                    threading.Thread(target=colortemp_loop, args=(client, topic_pub), daemon=True).start()
            elif action == "arrow_right_release":
                running = False


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    for tpDict in kTopicsDictList:
        client.subscribe(tpDict['topic_sub']+'/#')


def zb2wled(host, port, username, password):
    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message
    mqttc.username_pw_set(username=username, password=password)
    mqttc.connect(host=host, port=port, keepalive=60)

    # Blocking call that processes network traffic, dispatches callbacks and handles reconnecting.
    mqttc.loop_forever()

def main(argv=None):
    if sys.version_info < REQUIRED_PYTHON_VERSION:
        print(f'Requires python {REQUIRED_PYTHON_VERSION} or newer.', file=sys.stderr)
        return 1

    parser = argparse.ArgumentParser(description='Translate Zigbee MQTT to wled MQTT')

    required_parser = parser.add_argument_group('required arguments')
    required_parser.add_argument('-u', '--username', metavar='user', type=str, required=True, help=f'username for MQTT host to publish')
    required_parser.add_argument('-p', '--password', metavar='pwd', type=str, required=True, help=f'password for MQTT user')
    parser.add_argument('-H', '--host', metavar='host', type=str, default=defaultHost, help=f'MQTT host (default: {defaultHost})')
    parser.add_argument('-P', '--port', metavar='port', type=int, default=defaultPort, help=f'MQTT port (default: {defaultPort})')
    
    args = parser.parse_args(args=argv)
    zb2wled(**vars(args))
    return 0

if __name__ == '__main__':
    sys.exit(main())

