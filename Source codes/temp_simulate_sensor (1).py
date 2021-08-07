#!/usr/bin/env python3
# import necessary modules
import os
import dweepy
import time
import random
import requests
import EmulateGPIO as GPIO
import json
import paho.mqtt.client as mqtt

_ = os.system("clear")

#mqtt
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


def mqttUpdate(appliance, temp, topic):
	Data = {}
	Data['appliance'] = appliance
	Data['temp'] = temp
	DataJson = json.dumps(Data)
	print("Publishing data to mqtt... ")
	publishToTopic(topic, DataJson)

#telegram notification
#--------------------------------------------------------------
def telegramText(Message):
    
    bot_token = '1922316795:AAEH7LfWPNFExSpkUepA1EtFyE36dunMC0U'
    bot_chatID = '-1001525214257'
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + Message

    response = requests.get(send_text)

    return response.json()
#--------------------------------------------------------------

# ===============================
myThing = "temp_change_sensor"  # label for communication with dweet.io
# ===============================

# Setup hardware
# Set the desired pin numbering scheme:
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Create variables for the GPIO PINs the LEDs are connected to
# ============================================
# the PIN of the green LED
GreenLEDPin = 20  # Add values: add the pin number for the green LED
# the PIN of the red LED
RedLEDPin = 21  # Add values: add the pin number for the red LED
# =============================================

# Setup the direction of the GPIO pins - either INput or OUTput
# The PINs that connect LEDs must be set to OUTput mode:
# Prepare for initilization
GPIO.setup(GreenLEDPin, GPIO.OUT)
GPIO.setup(RedLEDPin, GPIO.OUT)
GPIO.output(GreenLEDPin, False)  # True = set 3.3V on the pin
GPIO.output(RedLEDPin,   False)  # False = set 0V on the pin
print('All LEDs are turned OFF' + '\n')
print(" ")
appliance = "tempSensor"

# main function
def getCurrentTemp():

    global appliance
    global topic

    GPIO.output(GreenLEDPin, False)  # False = set 0V on the pin
    GPIO.output(RedLEDPin,   True)  # True = set 3.3V on the pin
    print("Activate Red LED") # Red LED for Standby Mode
    print(" ")

    for i in range(4):
        # auto generate temp for input
        tempRange = str(random.randrange(20, 35))

        # print temperature from input
        print("The current temperature is " + (tempRange) + ' degrees.')
        newTempRange = int(tempRange)

        GPIO.output(GreenLEDPin, True)  # True = set 3.3V on the pin
        GPIO.output(RedLEDPin,   False)  # False = set 0V on the pin
        print("Activate Green LED") # Green LED for Checking Temperature (working)

        # conditional statements
        if newTempRange >= 30 and newTempRange <= 35:
            category = "HOT"
            telegramText("The temperature is " + tempRange + " degrees and is categorized as " + category + " and it is recommended for you to turn on your aircon.")
        elif newTempRange >= 26 and newTempRange <= 29:
            category = "AVERAGE"
            telegramText("The temperature is " + tempRange + " degrees and is categorized as " + category + " and it is recommended for you to turn on the aircon if you're feeling warm.")
        elif newTempRange >= 23 and newTempRange <= 25:
            category = "GETTING COLD"
            telegramText("The temperature is " + tempRange + " degrees and is categorized as " + category + " and it is recommended for you to turn off your aircon if you're feeling cold.")
        elif newTempRange <= 22:
            category = "COLD"
            telegramText("The temperature is " + tempRange + " degrees and is categorized as " + category + " and it is recommended for you to turn off your aircon.")
        
        mqttUpdate(appliance,newTempRange,topic)
        send_dweet = dweepy.dweet_for(myThing, {"category": category,"temperature": newTempRange}) # this function sends data to dweet.io
        dweet_created = send_dweet['created'] # get the time stamp of the first dweet
        print("send dweet@" + dweet_created + "\n")
        urlLive = "http://172.19.0.13:8080/add/" + "tempSensor" + "?temp=" + str(newTempRange) + "&category=" + category
        print(urlLive) 
        print(requests.put(urlLive))
        time.sleep(5)

    GPIO.output(GreenLEDPin, False) # True = set 3.3V on the pin
    GPIO.output(RedLEDPin,   False) #False = set 0V on the pin
    print('Deactivate All LEDs' + '\n') #close all LEDs after process finishes

getCurrentTemp()  # call function