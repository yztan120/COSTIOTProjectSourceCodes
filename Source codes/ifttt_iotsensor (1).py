#!/usr/bin/env python3
#import necessary modules
import os
import dweepy
import time
import EmulateGPIO as GPIO
import requests
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

# ===================
myThing = "temp_change_sensor"  # Add value: add your dweet thing name
# ===================

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
# Prepare for initialization
GPIO.setup(GreenLEDPin, GPIO.OUT)
GPIO.setup(RedLEDPin, GPIO.OUT)
GPIO.output(GreenLEDPin, False)  # True = set 3.3V on the pin
GPIO.output(RedLEDPin,   False)  # False = set 0V on the pin
print('All LEDs are turned OFF' + '\n')
appliance = "airconRemote"

while True:

    # Asks the user to select the LED. Put the response into a variable.
    startProg = input("Enter (s) to start or (q) to quit: ")

    # convert the input to lowercase and put it in another variable.
    startProg1 = startProg.lower()

    # start program [ red = standby, green = active]
    if startProg1 == "s":  
        print("Activate Red LED")
        GPIO.output(GreenLEDPin, False)  # False = set 0V on the pin
        GPIO.output(RedLEDPin,   True)  # True = set 3.3V on the pin
        print('sending dweet...')
        old_dweet = dweepy.dweet_for(myThing, {"dweet": "Red"}) # this function sends data to dweet.io
        old_created = old_dweet['created'] # get the time stamp of the first dweet
        print('send dweet@', old_created + '\n')
        #set default current temp to 24
        currentTemp = 24
        break

    elif startProg1 == "q":  # If the user chose to quit the program
        GPIO.output(GreenLEDPin, False)  # False = set 0V on the pin
        GPIO.output(RedLEDPin,   False)  # False = set 0V on the pin
        print('Deactivate All LEDs' + '\n')
        exit()

    else:  # If the user entered something other than r or q.
        print("Please enter (s) to start or (q) to quit.")

counter = 0

while True:
    new_dweet = dweepy.get_latest_dweet_for(myThing)  # get latest dweet
    new_created = new_dweet[0]["created"] # put the created value of the lastest dweet into a variable
    if new_created != old_created:  # check to see if the the old dweet is different from the new dweet
        counter += 1
        print(str(counter) + " New dweet detected!")
        old_created = new_created
        temp_action = (new_dweet[0]["content"]["temp_action"])
        mqttUpdate(appliance,temp_action,topic)
        print(temp_action)

        increaseTemp = "Increased by 1 degree"
        decreaseTemp = "Decreased by 1 degree"

        if(temp_action) == "DecreaseTemp":
            currentTemp -= 1
            telegramText("(" + decreaseTemp + ")" + " Current Temperature of Aircon is " + str(currentTemp))
            urlLive = "http://172.19.0.13:8080/add/" + "airconRemote" + "?temp_action=" + temp_action
            print(urlLive) 
            print(requests.put(urlLive))  
            time.sleep(5)
        elif(temp_action) == "IncreaseTemp":
            currentTemp += 1
            telegramText("(" + increaseTemp + ")" + " Current Temperature of Aircon is " + str(currentTemp))
            urlLive = "http://172.19.0.13:8080/add/" + "airconRemote" + "?temp_action=" + temp_action
            print(urlLive) 
            print(requests.put(urlLive))
            time.sleep(5)
        else:
            #for debugging purpose
            print("error")
            
        startProg1 == "s"
        print('receive new dweet@', new_created)
        print("Activate Green LED")
        GPIO.output(GreenLEDPin, True)
        GPIO.output(RedLEDPin,   False)
        print()

        time.sleep(5)  # after 5 second delay, set LED back to red

        print("Activate Red LED")
        GPIO.output(GreenLEDPin, False)  # False = set 0V on the pin
        GPIO.output(RedLEDPin,   True)  # True = set 3.3V on the pin
        print()