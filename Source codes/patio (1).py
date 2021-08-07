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
def yusufTelegramText(Message):
    
    bot_token = '1922316795:AAEH7LfWPNFExSpkUepA1EtFyE36dunMC0U'
    bot_chatID = '-1001525214257'
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + Message

    response = requests.get(send_text)

    return response.json()
#--------------------------------------------------------------
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


def mqttUpdate(appliance, statusappliance, shadeCovered, editedBy, topic):
	Data = {}
	Data['appliance'] = appliance
	Data['status'] = statusappliance
	Data['shadeCovered'] = shadeCovered
	Data['editedBy'] = editedBy
	DataJson = json.dumps(Data)
	print("Publishing data to mqtt... ")
	publishToTopic(topic, DataJson)
#--------------------------------------------------------------
_=os.system("clear")
def nl():
	print('\n')

#--------------------------------------------------------------
myThing = "yusufPatioShade"
#--------------------------------------------------------------

#--------------------------------------------------------------
# #setting up GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
_=os.system("clear")

#shade
patioShade50Pin = 1
GPIO.setup(patioShade50Pin, GPIO.OUT)
GPIO.output(patioShade50Pin,   False) #True = set 3.3V on the pin. 
                                #False = set 0V on the pin.

patioShade75Pin = 2
GPIO.setup(patioShade75Pin, GPIO.OUT)
GPIO.output(patioShade75Pin,   False) #True = set 3.3V on the pin. 
                                #False = set 0V on the pin.

patioShade100Pin = 3
GPIO.setup(patioShade100Pin, GPIO.OUT)
GPIO.output(patioShade100Pin,   False) #True = set 3.3V on the pin. 
                                #False = set 0V on the pin.

appliance = "Kupton Retractable Patio Shade"
statusappliance = "OFF"
shadeCovered = 0 #50/75/100
editedBy = "Yusuf"


_=os.system("clear") #clear screen/terminal
##################################################################

print (tabulate([[appliance, statusappliance, shadeCovered]], ["appliance", "statusappliance", "shadeCovered"], tablefmt="grid"))
print (tabulate(["The Kupton Retractable Patio Shade is " + statusappliance]))
print('----------------------------------------------------------')
print('Dweeting in progress (Kupton Retractable Patio Shade)...')

old_dweet = dweepy.dweet_for(myThing, {"status": statusappliance, "covered" : shadeCovered, "editedBy" : editedBy }) 
old_created = old_dweet['created'] #get the time stamp of the first dweet
print('Dweet successfully sent @' , old_created + '\n')
#http://172.19.0.13:8080/update/kuptonShade?status=OFF&covered=0&editedBy=Yusuf
#http://172.19.0.13:8080/add/kuptonShade?status=OFF&covered=0&editedBy=Yusuf
urlLive = "http://172.19.0.13:8080/add/" + "kuptonShade" + "?status=" + statusappliance + "&covered=%s" %shadeCovered + "&editedBy=" + editedBy
print(urlLive) 
print(requests.put(urlLive))



def dweetLoop():
    global old_dweet
    global old_created
    global appliance
    global statusappliance
    global shadeCovered
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
        newshadeCovered = new_dweet[0]["content"]["covered"]
        editedByShade = new_dweet[0]["content"]["editedBy"]
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
            print('Turn the Kupton Retractable Patio Shade ' + newstatusappliance)
            print('Set shade % to ' + str(newshadeCovered))
            #print(newhm)
            old_created = new_created


            if newstatusappliance == "ON":
                nl()
                statusappliance = "ON"
                shadeCovered = "50"
                mqttUpdate(appliance, statusappliance, shadeCovered, editedByShade, topic)
                print("Your Kupton Retractable Patio Shade has been updated!")
                print (tabulate([[appliance, statusappliance, shadeCovered]], ["Appliance", "Appliance Status", "Shade % Covered"], tablefmt="grid"))
                print (tabulate(["The Kupton Retractable Patio Shade is " + statusappliance]))
                yusufTelegramText("The Kupton Retractable Patio Shade is " + statusappliance + " and " + shadeCovered + "% covered")
                GPIO.output(patioShade50Pin, True)
                GPIO.output(patioShade75Pin, False)
                GPIO.output(patioShade100Pin, False)
            elif newstatusappliance == "ON2":
                nl()
                statusappliance = "ON"
                shadeCovered = "75"
                mqttUpdate(appliance, statusappliance, shadeCovered, editedByShade, topic)
                print("Your Kupton Retractable Patio Shade has been updated!")
                print (tabulate([[appliance, statusappliance, shadeCovered]], ["Appliance", "Appliance Status", "Shade % Covered"], tablefmt="grid"))
                print (tabulate(["The Kupton Retractable Patio Shade is " + statusappliance]))
                yusufTelegramText("The Kupton Retractable Patio Shade is " + statusappliance + " and " + shadeCovered + "% covered")
                GPIO.output(patioShade50Pin, False)
                GPIO.output(patioShade75Pin, True)
                GPIO.output(patioShade100Pin, False)
            elif newstatusappliance == "ON3":
                nl()
                statusappliance = "ON"
                shadeCovered = "100"
                mqttUpdate(appliance, statusappliance, shadeCovered, editedByShade, topic)
                print("Your Kupton Retractable Patio Shade has been updated!")
                print (tabulate([[appliance, statusappliance, shadeCovered]], ["Appliance", "Appliance Status", "Shade % Covered"], tablefmt="grid"))
                print (tabulate(["The Kupton Retractable Patio Shade is " + statusappliance]))
                yusufTelegramText("The Kupton Retractable Patio Shade is " + statusappliance + " and " + shadeCovered + "% covered")
                GPIO.output(patioShade50Pin, False)
                GPIO.output(patioShade75Pin, False)
                GPIO.output(patioShade100Pin, True)
            elif newstatusappliance == "OFF":
                nl()
                statusappliance = "OFF"
                shadeCovered = "0"
                mqttUpdate(appliance, statusappliance, shadeCovered, editedByShade, topic)
                print("Your Kupton Retractable Patio Shade has been updated!")
                print (tabulate([[appliance, statusappliance, shadeCovered]], ["Appliance", "Appliance Status", "Shade % Covered"], tablefmt="grid"))
                print (tabulate(["The Kupton Retractable Patio Shade is " + statusappliance]))
                yusufTelegramText("The Kupton Retractable Patio Shade is " + statusappliance + " and " + shadeCovered + "% covered")
                GPIO.output(patioShade50Pin, False)
                GPIO.output(patioShade75Pin, False)
                GPIO.output(patioShade100Pin, False)


def main():
    dweetLoop()
main()