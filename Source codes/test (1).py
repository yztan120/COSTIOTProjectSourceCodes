#!/bin/python3

#Dependencies
import ssl
ssl.match_hostname = lambda cert, hostname: True
import dweepy
import EmulateGPIO as GPIO
from IPython.display import clear_output
import time
import os
import sys
from tabulate import tabulate
import random
import requests
import paho.mqtt.client as mqtt
import random, threading, json
from datetime import datetime

####################






#NEW
#====================================================
# MQTT shit 
MQTT_Broker = "172.19.0.12"
MQTT_Port = 1883
Keep_Alive_Interval = 45
topic = "Cost/Sensors"

def on_connect(client, userdata, rc):
	if rc != 0:
		pass
		print("Unable to connect to MQTT Broker...")
	else:
		print("Connected with MQTT Broker: " + str(MQTT_Broker))

def on_publish(client, userdata, mid):
	pass
		
def on_disconnect(client, userdata, rc):
	if rc !=0:
		pass
		
mqttc = mqtt.Client()
mqttc.on_connect = on_connect
mqttc.on_disconnect = on_disconnect
mqttc.on_publish = on_publish
mqttc.tls_set('/root/iot_vol/iotsec/cacert/crt/ca.crt')
mqttc.username_pw_set("cost", password="cost")
mqttc.connect(MQTT_Broker, int(MQTT_Port), int(Keep_Alive_Interval))		

		
def publishToTopic(topic, message):
	mqttc.publish(topic,message)
	print ("Published: " + str(message) + " " + "on MQTT Topic: " + str(topic))
	print("")


def updateFanMqtt(applianceFan, statusFan, speedFan, editedBy, topic):
	fanData = {}
	fanData['appliance'] = applianceFan
	fanData['status'] = statusFan
	fanData['speed'] = speedFan
	fanData['editedBy'] = editedBy
    #fanData['editedBy'] = editedBy
    #fanData['editedby'] = editedBy
	#Humidity_Data['Date'] = (datetime.today()).strftime("%d-%b-%Y %H:%M:%S:%f")
	fanDataJson = json.dumps(fanData)
	print("Publishing fan data... ")
	publishToTopic(topic, fanDataJson)



#====================================================






updateFanMqtt("patio", "statusFan", "speedFan", "editedByFan", "Cost/Sensors")