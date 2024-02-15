#!/usr/bin/python3

import os, sys
import time
import RPi.GPIO as GPIO
#import paho.mqtt.client as mqtt

EXPORT101="rm /root/low.txt"
EXPORT102="/root/ise_console_low2"
EXPORT201="rm /root/high.txt"
EXPORT202="/root/ise_console_high2"
EXPORT301="rm /root/sample.txt"
EXPORT302="/root/ise_console_sample2"


#broker_address="192.168.1.85"
#mqttc = mqtt.Client("pump_client")
#mqttc.connect(broker_address, 1883)

#global com


high = 36
low = 35
sample = 37
drainage = 38

# open the gpio chip as board mode
GPIO.setmode(GPIO.BOARD)

#set pins as ouput
GPIO.setup(high, GPIO.OUT)
GPIO.setup(low, GPIO.OUT)
GPIO.setup(sample, GPIO.OUT)
GPIO.setup(drainage, GPIO.OUT)

# variables for running time
# flow rate
# drainage volume should be larger than low volume
# low volume should be larger than sampling volume
# sample volume should be larger than high volume

high_t = 5
low_t = 5
sample_t = 5
drainage_t = 5

try:
	#low
	GPIO.output(low, GPIO.LOW) #when low, led turned on
	#state_low = GPIO.input(low)
	#print("state_low: ", state_low)
	time.sleep(low_t)
	GPIO.output(low, GPIO.HIGH)
	#state_low = GPIO.input(low)
	#print("state_low: ", state_low)
			
	com = 'l'
	print("low measurement request publish", com)
	#mqttc.publish("command/low", com)
	#mqttc.loop(2)
	time.sleep(5)

	#############################
	os.system(EXPORT101)
	first_start = time.time()

	for i in range(0,50):
		start = time.time()
		os.system(EXPORT102)
		#time.sleep(0.5)
		end = time.time()
		print(end - start)

	last_end = time.time()
	print("low measurement done")
	print(last_end - first_start)
	time.sleep(5)
	###############################

	#high
	GPIO.output(high, GPIO.LOW) #when low, led turned on
	#state_low = GPIO.input(low)
	#print("state_low: ", state_low)
	time.sleep(high_t)
	GPIO.output(high, GPIO.HIGH)
	#state_low = GPIO.input(low)
	#print("state_low: ", state_low)

	#com = 'h'
	print("high measurement request publish", com)
	#mqttc.publish("command/high", com)
	#mqttc.loop(2)
	time.sleep(5)

	#############################
	os.system(EXPORT201)
	first_start = time.time()

	for i in range(0,50):
		#start = time.time()
		os.system(EXPORT202)
		#time.sleep(0.5)
		#end = time.time()
		#print(end - start)

	last_end = time.time()
	print("high measurement done")
	print(last_end - first_start)
	time.sleep(5)
	###############################

	#sample
	GPIO.output(sample, GPIO.LOW) #when low, led turned on
	#state_low = GPIO.input(low)
	#print("state_low: ", state_low)
	time.sleep(sample_t)
	GPIO.output(sample, GPIO.HIGH)
	#state_low = GPIO.input(low)
	#print("state_low: ", state_low)

	com = 's'
	print("sample measurement request publish", com)
	#mqttc.publish("command/sample", com)
	#mqttc.loop(2)
	time.sleep(5)

	#############################
	os.system(EXPORT301)
	first_start = time.time()

	for i in range(0,50):
		#start = time.time()
		os.system(EXPORT302)
		#time.sleep(0.5)
		#end = time.time()
		#print(end - start)

	last_end = time.time()
	print("sample measurement done")
	print(last_end - first_start)
	time.sleep(5)
	###############################

	#drainage
	GPIO.output(drainage, GPIO.HIGH) #when low, led turned on
	#state_low = GPIO.input(low)
	#print("state_low: ", state_low)
	time.sleep(drainage_t)
	GPIO.output(drainage, GPIO.HIGH)
	#state_low = GPIO.input(low)
	#print("state_low: ", state_low)

	com = 'd'
	print("drainage measurement request publish", com)
	#mqttc.publish("command/drainage", com)
	#mqttc.loop(2)
	time.sleep(5)

	#exit
	GPIO.output(high, GPIO.HIGH)
	GPIO.output(low, GPIO.HIGH)
	GPIO.output(sample, GPIO.HIGH)
	GPIO.output(drainage, GPIO.HIGH)
	#GPIO.cleanup()
	#print("state_low: ", state_low)
	time.sleep(drainage_t)
	GPIO.output(drainage, GPIO.HIGH)
	#state_low = GPIO.input(low)
	#print("state_low: ", state_low)

	com = 'd'
	print("drainage measurement request publish", com)
	#mqttc.publish("command/drainage", com)
	#mqttc.loop(2)
	time.sleep(5)

	#exit
	GPIO.output(high, GPIO.HIGH)
	GPIO.output(low, GPIO.HIGH)
	GPIO.output(sample, GPIO.HIGH)
	GPIO.output(drainage, GPIO.HIGH)
	#GPIO.cleanup()

except KeyboardInterrupt:
	GPIO.output(high, GPIO.HIGH)
	GPIO.output(low, GPIO.HIGH)
	GPIO.output(sample, GPIO.HIGH)
	GPIO.output(drainage, GPIO.HIGH)
	#GPIO.cleanup()

'''
com = 'q'
mqttc.publish("command/quit", com)
time.sleep(2)
mqttc.loop(2)
'''

'''
try:
	while True:
		GPIO.output(high, GPIO.LOW) #when low, led turned on
		GPIO.output(low, GPIO.LOW)
		GPIO.output(sample, GPIO.LOW)
		GPIO.output(drainage, GPIO.LOW)
		
		state_high = GPIO.input(high)
		state_low = GPIO.input(low)
		state_sample = GPIO.input(sample)
		state_drainage = GPIO.input(drainage)
		print("state_high: ", state_high)
		print("state_low: ", state_low)
		print("state_sample: ", state_sample)
		print("state_drainage: ", state_drainage)
		
		time.sleep(5)
		
		GPIO.output(high, GPIO.HIGH)
		GPIO.output(low, GPIO.HIGH)
		GPIO.output(sample, GPIO.HIGH)
		GPIO.output(drainage, GPIO.HIGH)
		
		state_high = GPIO.input(high)
		state_low = GPIO.input(low)
		state_sample = GPIO.input(sample)
		state_drainage = GPIO.input(drainage)
		print("state_high: ", state_high)
		print("state_low: ", state_low)
		print("state_sample: ", state_sample)
		print("state_drainage: ", state_drainage)
		time.sleep(5)
		
except KeyboardInterrupt:
	GPIO.output(high, GPIO.LOW)
	GPIO.output(low, GPIO.LOW)
	GPIO.output(sample, GPIO.LOW)
	GPIO.output(drainage, GPIO.LOW)
	GPIO.cleanup()
'''
