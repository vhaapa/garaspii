#!/usr/bin/env python

import sys
import time
import grovepi          #grovepi.py file, code for sensors and arduino board
#import threading
import twitter
import keys 		#keys.py with keys to different APIs
from picamera import PiCamera


#functions

def blinkLed(pin, sleep):	#led on... led off
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

def resetActor(actor):		#reset all output actors e.g. leds 
	grovepi.digitalWrite(actor,0)
	return

def connectTwitter():		#connect to twitter and print it
	api = twitter.Api(consumer_key=keys.twitterCK(),consumer_secret=keys.twitterCS(),access_token_key=keys.twitterATK(),access_token_secret=keys.twitterATS())
	print "Twitter connected!"
	return api

def measureDistance(ultrasonic):		#ultrasonic measurement
	distance = grovepi.ultrasonicRead(ultrasonic)
	return distance

def setupLed(led):
	grovepi.pinMode(led,"OUTPUT")
	resetActor(led)
	return

def takePhoto():
	filepath = "/home/pi/pics/" + time.strftime("%Y%m%d-%H%M%S") + ".jpg" 
	cam = PiCamera()
	cam.start_preview()
	time.sleep(2)
	cam.capture(filepath)
	cam.stop_preview()
	cam.close()
	return filepath

def checkTime(current, last, limit):
	if current - last > limit:
		return True
	else:
		return False

# setting up...
# pins, sensors and actors
led = {"red":6, "blue":5, "green":7}
#blue = 5
#red = 6
#green = x 
button = 2
temphum = 4
ultrasonic = 8

# variables
temp, hum, dist = 0, 0, 0
#hum = 0
api = connectTwitter()   #create a twitter connection
#dist= 0
#message = ["Status:", "Door open?", "ALERT!", "Ok?"] 
msg = "Status:"
startStatus = time.time() 	#used as timer
startTemphum = time.time()	#used as timer
door = True		#door closed = true, open = false
doorLogic = True	#variable used with  door status changes
photoTaken = False	#used for photo logic
photoTime = time.time() #last picture taken, used as timer

# main program

# setup and reset leds
for k in led:
	blinkLed(led[k],1)
	setupLed(led[k])
	print k + " led setup done."

while True:
	try:

# button to break loop and end the program

		if pushButton(button):
			for k in led:
				resetActor(led[k])
			print ("Button pushed, The End!")
			api.PostUpdate("Button pushed, The End. Bye!")
			break

# measure distance from door

		dist = measureDistance(ultrasonic)
		if dist == 65535:	#read again if return value is "non-readable"
			dist = measureDistance(ultrasonic)

# actions based on distance

		if dist < 120:
			door = True
			resetActor(led["blue"])
			resetActor(led["green"])
			grovepi.digitalWrite(led["red"],31)
			msg = "MOTION!"
			if photoTaken == False and checkTime(time.time(),photoTime,300):
#				photo = takePhoto()
				photoTime = time.time()
#                               print "ZAP: " + photo 
				print "ZAP"
				photoTaken = True
#				api.PostUpdate("Meedio", media=photo)
		elif dist >= 120 and dist < 140:
			door = True
			msg = "OK?"
			resetActor(led["red"])
			resetActor(led["green"])
			grovepi.digitalWrite(led["blue"],31)
			photoTaken = False
		else:
			door =False
			msg = "Door open!"
			resetActor(led["red"])
			resetActor(led["blue"])
			grovepi.digitalWrite(led["green"],31)
			photoTaken = False

# door open or closed, tweet if changed

		if door != doorLogic:
			api.PostUpdate("{} {} Dist= {} cm".format(time.ctime(),msg,dist)) #tweet results
			doorLogic = door

# measure temp and hum every app. 2 hours and tweet update or alert

		if time.time() - startTemphum >= 300:
			[t, h] = grovepi.dht(temphum,0)
			startTemphum = time.time()
			if abs(temp - t) >= 3 or abs(hum - h) >= 5:
				msg = "ALERT!"
				api.PostUpdate("{} {} Temp= {} C, Hum= {} %, Dist= {} cm ".format(time.ctime(),msg,t,h,dist))
				temp = t
				hum = h
	 		elif time.time() - startStatus >= 3600: 
				msg = "Status:"
				api.PostUpdate("{} {} Temp= {} C, Hum= {} %, Dist= {} cm ".format(time.ctime(),msg,t,h,dist))
				startStatus = time.time()
			else:
				pass

# exceptions

	except KeyboardInterrupt as error:
		for k in led:
			resetActor(led[k])
		print "Keyboard Interrupt", str(error)
		break

	except (IOError,TypeError) as error:
		print "Mystical Error", str(error)

	except twitter.error.TwitterError as error:
		pass

sys.exit()

#
