#!/usr/bin/env python

import sys
import time
import grovepi
import threading
import twitter
import keys 		#own file keys.py with keys to different APIs

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

def resetAll():			#reset all output actors e.g. leds 
	grovepi.digitalWrite(5,0)
	return

def repeatTime():		#timed actions and repeats, ATM prints repet every 5 secs
	if not pushButton(button): 
		threading.Timer(5.0, repeatTime).start()
		print ("Repeat")
	else:
		return

def connectTwitter():		#connect to twitter and print it
	api = twitter.Api(consumer_key=keys.twitterCK(),consumer_secret=keys.twitterCS(), access_token_key=keys.twitterATK(), access_token_secret=keys.twitterATS())
	print "Twitter connected!"
	return api

#pins, sensors and actors
blue = 5
button = 2
temphum = 4

#variables
temp = 0
hum = 0
api = connectTwitter()   #create a twitter connection


#main program

repeatTime()	#for testing timed repeted actions


while True:
	try:
		ledBlink(blue,2)		#testing that loop is working

		if pushButton(button):		#break loop and end the program
			print ("Button pushed, The End!")
			break

#measure temp and hum and print if changed

		[t, h] = grovepi.dht(temphum,0)
		if temp != t or hum != h:
			temp = t
			hum = h
			print "Temperature = {} C, Humadity = {} %".format(temp, hum)
			api.PostUpdate("{} Status OK. Temp= {}  C, Hum=  {} % ".format(time.ctime(),temp, hum))		#tweet results

#exceptions

	except KeyboardInterrupt as error:
		resetAll()
		print "Keyborad Interrupt", str(error)
		break

	except (IOError,TypeError) as error:
		print "Mystical Error", str(error)

	except twitter.error.TwitterError as error:
		pass

sys.exit()

#
