#!/usr/bin/env python

import sys
import time
import grovepi
import threading

#functions

def ledBlink(pin, sleep):
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

def repeatTime():		#timed actions and repeats
	if not pushButton(button): 
		threading.Timer(5.0, repeatTime).start()
		print ("Repeat")
	else:
		return

#pins, sensors and actors
blue = 5
button = 2
temphum = 4

#variables
repeat = 3.0
temp = 0
hum = 0

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
			print "Temperature = ", temp, "C\tHumadity = ", hum, "%"
		
#exceptions

	except KeyboardInterrupt as error:
		resetAll()
		print "Keyborad Interrupt", str(error)
		break

	except (IOError,TypeError) as error:
		print "Mystical Error", str(error)


sys.exit()

#
