#!/usr/bin/env python
#python version 2

import sys
import time
import grovepi
import threading
import twitter
import keys 		#own file keys.py with keys to different APIs
from picamera import PiCamera


#functions

def ledBlink(pin, sleep):	#led on... led off
	grovepi.pinMode(pin,"OUTPUT")
	grovepi.digitalWrite(pin,1)
	time.sleep(sleep)
	grovepi.digitalWrite(pin,0)
	time.sleep(sleep)
	return

def pushButton(pin):		#if button pushed, return True
	grovepi.pinMode(pin,"INPUT")
	if grovepi.digitalRead(pin):
		return True
	else:
		return False

def resetAll(led):		#reset all output actors e.g. leds 
	grovepi.digitalWrite(led,0)
	return

def repeatTime():		#timed actions and repeats, ATM prints repeat every 5 secs
	if not pushButton(button): 
		threading.Timer(5.0, repeatTime).start()
		print ("Repeat")
	else:
		return

def connectTwitter():		#connect to twitter and print it
	api = twitter.Api(consumer_key=keys.twitterCK(),consumer_secret=keys.twitterCS(),access_token_key=keys.twitterATK(),access_token_secret=keys.twitterATS())
	print "Twitter connected!"
	return api

def measureDistance(ultrasonic):		#ultrasonic measurement
	distance = grovepi.ultrasonicRead(ultrasonic)
	return distance

def setupLeds(blue, red):
	grovepi.pinMode(blue,"OUTPUT")
	grovepi.pinMode(red,"OUTPUT")
	resetAll(blue)
	resetAll(red)
	return "Led setup complete."

def takePhoto():
	filepath = "/home/pi/pics/" + time.strftime("%Y%m%d-%H%M%S") + ".jpg" 
	cam = PiCamera()
	cam.start_preview()
	time.sleep(2)
	cam.capture(filepath)
	cam.stop_preview()
	cam.close()
	return filepath

#pins, sensors and actors
blue = 5
red = 6
#green = x 
button = 2
temphum = 4
ultrasonic = 8

#variables
temp = 0
hum = 0
api = connectTwitter()   #create a twitter connection
dist= 0
msg = "Status:"
start = time.time() 	#used as timer
door = True		#door closed = true, open = false
doorLogic = True	#variable used with  door status changes

#main program

print setupLeds(blue,red)

#repeatTime()	#for testing timed repeted actions


while True:
	try:
#		print "BLAA"
#		ledBlink(red,2)		#testing that loop is working

		if pushButton(button):		#break loop and end the program
			resetAll(red)
			print ("Button pushed, The End!")
			break

#measure distance and print it, use red led

		dist = measureDistance(ultrasonic)
		if dist == 65535:	#read again if return value is "non-readable"
			dist = measureDistance(ultrasonic)

#		print dist, "cm"
		if dist < 100:
			grovepi.digitalWrite(red,31)
		else:
			resetAll(red)

#door open or closed, tweet if changed
		if dist > 100:
			door = False
			msg = "Door open!"
		else:
			door = True
			msg = "OK?"

		if door != doorLogic:
			[t, h] = grovepi.dht(temphum,0)
			temp = t
			hum = h
#			print "Temperature = {} C, Humidity = {} %".format(temp, hum)
			api.PostUpdate("{} {} Temp= {} C, Hum= {} %, Dist= {} cm ".format(time.ctime(),msg,temp,hum,dist))		#tweet results
			doorLogic = door
			if  door == False:
				photo = takePhoto()
				print "ZAP: " + photo

#measure temp and hum every app. 1 hour and tweet update or alert

		end  = time.time()
		if end - start >= 1800:
#			print "Temperature = {} C, Humidity = {} %".format(temp, hum)
			[t, h] = grovepi.dht(temphum,0)
			if temp != t or hum != h:
				msg = "ALERT!"
				temp = t
				hum = h
			else:
				msg = "Status:"
			api.PostUpdate("{} {} Temp= {} C, Hum= {} %, Dist= {} cm ".format(time.ctime(),msg,temp,hum,dist))
			start = time.time()

#exceptions

	except KeyboardInterrupt as error:
		resetAll(blue)
		resetAll(red)
		print "Keyboard Interrupt", str(error)
		break

	except (IOError,TypeError) as error:
		print "Mystical Error", str(error)

	except twitter.error.TwitterError as error:
		pass

sys.exit()

#
