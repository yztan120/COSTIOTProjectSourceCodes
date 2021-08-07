#!/bin/python3

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
#--------------------------------------------------------------

MQTT_Broker = "172.19.0.12"
MQTT_Port = 1883
Keep_Alive_Interval = 45
topic = "Cost/Sensors" 

def on_connect(client, userdata, rc):
	if rc != 0: #error code
		pass
		print("Unable to connect to MQTT Broker...")
	else:
		print("Connected with MQTT Broker: " + str(MQTT_Broker))

def on_publish(client, userdata, mid):
	pass
		
def on_disconnect(client, userdata, rc):
	if rc !=0:
		pass
		
mqttc = mqtt.Client() #initiate new connection
mqttc.on_connect = on_connect
mqttc.on_disconnect = on_disconnect
mqttc.on_publish = on_publish
mqttc.tls_set('/root/iot_vol/iotsec/cacert/crt/ca.crt') #use TLS 
mqttc.username_pw_set("cost", password="cost") #user authentication
mqttc.connect(MQTT_Broker, int(MQTT_Port), int(Keep_Alive_Interval))#connect

		
def publishToTopic(topic, message): #publishing to mqtt on the topic
	mqttc.publish(topic,message)
	print ("Published: " + str(message) + " " + "on MQTT Topic: " + str(topic))
	print("")


def mqttUpdate(appliance, statusappliance, tvChannel, editedBy, topic): # publishing json formatted data to mqtt over tls
	Data = {}
	Data['appliance'] = appliance
	Data['status'] = statusappliance
	Data['tvChannel'] = tvChannel
	Data['editedBy'] = editedBy
	DataJson = json.dumps(Data)
	print("Publishing data to mqtt... ")
	publishToTopic(topic, DataJson)
#--------------------------------------------------------------
_=os.system("clear")
def nl():
	print('\n')

#--------------------------------------------------------------
myThing = "yusufMatinYuzheTv"
#--------------------------------------------------------------

#--------------------------------------------------------------
# #setting up GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
_=os.system("clear")

#tv
tvOnChannel1 = 1
GPIO.setup(tvOnChannel1, GPIO.OUT)
GPIO.output(tvOnChannel1,   False) #True = set 3.3V on the pin. 
                                #False = set 0V on the pin.

tvOnChannel2 = 2
GPIO.setup(tvOnChannel2, GPIO.OUT)
GPIO.output(tvOnChannel2,   False) #True = set 3.3V on the pin. 
                                #False = set 0V on the pin.

tvOnChannel3 = 3
GPIO.setup(tvOnChannel3, GPIO.OUT)
GPIO.output(tvOnChannel3,   False) #True = set 3.3V on the pin. 
                                #False = set 0V on the pin.

appliance = "Samsung 80 Inch TV"
statusappliance = "OFF"
tvChannel = 0 #1/2/3
editedBy = "Yusuf"


_=os.system("clear") #clear screen/terminal
##################################################################

print (tabulate([[appliance, statusappliance, tvChannel]], ["appliance", "statusappliance", "tvChannel"], tablefmt="grid")) #shows current status
print (tabulate(["Samsung 80 Inch TV is " + statusappliance]))
print('----------------------------------------------------------')
print('Dweeting in progress (Samsung 80 Inch TV is)...')

old_dweet = dweepy.dweet_for(myThing, {"status": statusappliance, "tvChannel" : tvChannel, "editedBy" : editedBy }) # check for updates if any
old_created = old_dweet['created'] #get the time stamp of the first dweet
print('Dweet successfully sent @' , old_created + '\n')
urlLive = "http://172.19.0.13:8080/add/" + "samsungTv" + "?status=" + statusappliance + "&tvChannel=%s" %tvChannel + "&editedBy=" + editedBy
urlLogs = "http://172.19.0.13:8080/add/" + "samsungTv" + "?status=" + statusappliance + "&tvChannel=%s" %tvChannel + "&editedBy=" + editedBy
print(urlLive) 
print(requests.put(urlLive))
print(urlLogs) 
print(requests.put(urlLogs))



def dweetLoop():
    global old_dweet
    global old_created
    global appliance
    global statusappliance
    global tvChannel
    global editedBy
    global topic
    counter = 0
    global MQTT_Broker 
    global MQTT_Port 
    global Keep_Alive_Interval

    while True:
        time.sleep(10)
        new_dweet = dweepy.get_latest_dweet_for(myThing) #get latest dweet
        new_created = new_dweet[0]["created"] #put the created value of the lastest dweet into a variable
        newstatusappliance = new_dweet[0]["content"]["status"]
        newtvChannel = new_dweet[0]["content"]["tvChannel"]
        editedByTv = new_dweet[0]["content"]["editedBy"]
        if new_created != old_created: #check to see if the the old dweet is different from the new dweet
            mqttc = mqtt.Client()
            mqttc.on_connect = on_connect
            mqttc.on_disconnect = on_disconnect
            mqttc.on_publish = on_publish
            mqttc.tls_set('/root/iot_vol/iotsec/cacert/crt/ca.crt')
            mqttc.username_pw_set("cost", password="cost")
            mqttc.connect(MQTT_Broker, int(MQTT_Port), int(Keep_Alive_Interval))
            counter += 1
            _=os.system("clear") #clear screen/terminal
            #print("A New dweet detected! {" + str(counter) + "} ",end='\n')
            print('----------------------------------------------------------')
            print("A New remote command has been detected!",end='\n')
            #print(old_dweet)
            print('Request to:')
            print('Turn the Samsung TV ' + newstatusappliance)
            print('Set TV Channel % to ' + str(newtvChannel))
            #print(newhm)
            old_created = new_created


            if newstatusappliance == "ON":
                nl()
                statusappliance = "ON"
                tvChannel = "1"
                mqttUpdate(appliance, statusappliance, tvChannel, editedByTv, topic)
                print("Your Samsung TV has been updated!")
                print (tabulate([[appliance, statusappliance, tvChannel]], ["Appliance", "Appliance Status", "TV Channel"], tablefmt="grid"))
                print (tabulate(["The Samsung TV is " + statusappliance]))
                GPIO.output(tvOnChannel1, True)
                GPIO.output(tvOnChannel2, False)
                GPIO.output(tvOnChannel3, False)
            elif newstatusappliance == "ON2":
                nl()
                statusappliance = "ON"
                tvChannel = "2"
                mqttUpdate(appliance, statusappliance, tvChannel, editedByTv, topic)
                print("Your Samsung TV has been updated!")
                print (tabulate([[appliance, statusappliance, tvChannel]], ["Appliance", "Appliance Status", "TV Channel"], tablefmt="grid"))
                print (tabulate(["The Samsung TV is " + statusappliance]))
                GPIO.output(tvOnChannel1, False)
                GPIO.output(tvOnChannel2, True)
                GPIO.output(tvOnChannel3, False)
            elif newstatusappliance == "ON3":
                nl()
                statusappliance = "ON"
                tvChannel = "3"
                mqttUpdate(appliance, statusappliance, tvChannel, editedByTv, topic)
                print("Your Samsung TV has been updated!")
                print (tabulate([[appliance, statusappliance, tvChannel]], ["Appliance", "Appliance Status", "TV Channel"], tablefmt="grid"))
                print (tabulate(["The Samsung TV is " + statusappliance]))
                GPIO.output(tvOnChannel1, False)
                GPIO.output(tvOnChannel2, False)
                GPIO.output(tvOnChannel3, True)
            elif newstatusappliance == "OFF":
                nl()
                statusappliance = "OFF"
                tvChannel = "0"
                mqttUpdate(appliance, statusappliance, tvChannel, editedByTv, topic)
                print("Your Samsung TV has been updated!")
                print (tabulate([[appliance, statusappliance, tvChannel]], ["Appliance", "Appliance Status", "TV Channel"], tablefmt="grid"))
                print (tabulate(["The Samsung TV is " + statusappliance]))
                GPIO.output(tvOnChannel1, False)
                GPIO.output(tvOnChannel2, False)
                GPIO.output(tvOnChannel3, True)


def main():
    dweetLoop()
main()