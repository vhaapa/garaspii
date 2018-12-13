#!/usr/bin/env python

import sys
import time
import grovepi          #grovepi.py file, code for sensors and arduino board
#import threading
import twitter
import keys 		#keys.py with keys to different APIs
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

def resetActor(actor):		#reset all output actors e.g. leds 
	grovepi.digitalWrite(actor,0)
	return

#def repeatTime():		#timed actions and repeats, ATM prints repeat every 5 secs
#	if not pushButton(button): 
#		threading.Timer(5.0, repeatTime).start()
#		print ("Repeat")
#	else:
#		return

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

# setting up...
# pins, sensors and actors
led = {"red":6, "blue":5, "green":3}
#blue = 5
#red = 6
#green = x 
button = 2
temphum = 4
ultrasonic = 8

# variables
temp = 0
hum = 0
api = connectTwitter()   #create a twitter connection
dist= 0
#message = ["Status:", "Door open?", "ALERT!", "Ok?"] 
msg = "Status:"
start = time.time() 	#used as timer
door = True		#door closed = true, open = false
doorLogic = True	#variable used with  door status changes
photoTaken = False	#used for photo logic
photoTime = time.time() #last picture taken, used as timer

#main program

#print setupLeds(led["blue"],led["red"])
#setup leds
for k in led:
	setupLed(led[k])
	print k + " led setup done."

#repeatTime()	#for testing timed repeted actions


while True:
	try:
#		print "BLAA"
#		ledBlink(red,2)		#testing that loop is working

		if pushButton(button):		#break loop and end the program
			for k in led:
				resetActor(led[k])
			print ("Button pushed, The End!")
			api.PostUpdate("Button pushed, The End. Bye!")
			break

#measure distance and print it, use red led

		dist = measureDistance(ultrasonic)
		if dist == 65535:	#read again if return value is "non-readable"
			dist = measureDistance(ultrasonic)

#		print dist, "cm"
		if dist < 120:
			door = False
			grovepi.digitalWrite(led["red"],31)
			msg = "MOTION"
			if photoTaken == False and time.time() - photoTime > 300:			
				photo = takePhoto()
				photoTime = time.time()
                               	print "ZAP: " + photo 
			#	print "PHOTO"
				photoTaken = True
				api.PostUpdate("Meedio", media=photo)
		elif dist >= 120 and dist < 130:
			door = True
			msg = "OK?"
			resetActor(led["red"])
			photoTaken = False
		else:
			door =False
			msg = "Door open!"
			resetActor(led["red"])
			photoTaken = False

#door open or closed, tweet if changed
#		if dist > 120:
#			door = False
#			msg = "Door open!"
#		else:
#			door = True
#			msg = "OK?"

		if door != doorLogic:
			[t, h] = grovepi.dht(temphum,0)
			temp = t
			hum = h
#			print "Temperature = {} C, Humidity = {} %".format(temp, hum)
			api.PostUpdate("{} {} Temp= {} C, Hum= {} %, Dist= {} cm ".format(time.ctime(),msg,temp,hum,dist))		#tweet results
			doorLogic = door
#			if  door == False:
#				photo = takePhoto()
#				print "ZAP: " + photo

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
