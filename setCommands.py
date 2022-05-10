#!/usr/bin/env python3

import paho.mqtt.client as mqtt
from time import sleep

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("topic/EV3")

pub=None

client = mqtt.Client()
client.connect("localhost",1883,60)

client.on_connect = on_connect

client.loop_start()

sleep(0.1)

run=True
while run:
    pub=input("Comando: ")
    if pub=="Q":
        run=False
    else:
        client.publish("topic/EV3", pub)

client.disconnect()