#!/usr/bin/python3

import os, sys
import time
import RPi.GPIO as GPIO

EXPORT101="rm /home/kjh/Desktop/ise_code/low.txt"
EXPORT102="/root/ise_console_low2"
EXPORT201="rm /home/kjh/Desktop/ise_code/high.txt"
EXPORT202="/root/ise_console_high2"
EXPORT301="rm /home/kjh/Desktop/ise_code/sample.txt"
EXPORT302="/root/ise_console_sample2"

high = 36
low = 35
sample = 37
drainage = 38

# open the gpio chip as board mode
GPIO.setmode(GPIO.BOARD)

#set pins as output
GPIO.setup(high, GPIO.OUT)
GPIO.setup(low, GPIO.OUT)
GPIO.setup(sample, GPIO.OUT)
GPIO.setup(drainage, GPIO.OUT)

# variables for running time
# flow rate
# drainage volume should be larger than low volume
# low volume should be larger than sampling volume
# sample volume should be larger than high volume

#high_t = 14.43
# high_t = 16.43
high_t = 30
#low_t = 21.43
# low_t = 23.43
low_t = 30
rinse_t = low_t
#sample_t = 19.5
sample_t = 24.5
drainage_t = 50

measure_time = 180

def low_measurement():
	GPIO.output(low, GPIO.LOW); time.sleep(low_t)
	GPIO.output(low, GPIO.HIGH); time.sleep(180) # edit 60 to 180

	os.system(EXPORT101)
	first_start = time.time()
	for i in range(0,10):   # edit 5 to 10
		os.system(EXPORT102)
	last_end = time.time()
	print("low measurement done: ", last_end - first_start, "sec"); time.sleep(5)

def high_measurement():
	GPIO.output(high, GPIO.LOW); time.sleep(high_t)
	GPIO.output(high, GPIO.HIGH); time.sleep(180) # edit 60 to 180

	os.system(EXPORT201)
	first_start = time.time()
	for i in range(0,10):  # edit 5 to 10
		os.system(EXPORT202)
	last_end = time.time()
	print("high measurement done: ", last_end - first_start, "sec"); time.sleep(5)

def sample_measurement():
	GPIO.output(sample, GPIO.LOW); time.sleep(sample_t)
	GPIO.output(sample, GPIO.HIGH); time.sleep(180) # edit 60 to 180

	os.system(EXPORT301)
	first_start = time.time()
	for i in range(0,10): # edit 5 to 10
		os.system(EXPORT302)
	last_end = time.time()
	print("sample measurement done: ", last_end - first_start, "sec"); time.sleep(5)

def drain():
	GPIO.output(drainage, GPIO.LOW); time.sleep(drainage_t)
	GPIO.output(drainage, GPIO.HIGH); time.sleep(5)

def rinse():
	GPIO.output(low, GPIO.LOW); time.sleep(rinse_t)
	GPIO.output(low, GPIO.HIGH); time.sleep(15)

def rinse_using_sample():
	GPIO.output(sample, GPIO.LOW); time.sleep(rinse_t)
	GPIO.output(sample, GPIO.HIGH); time.sleep(15)

try:
	#before beginning
	drain()
	rinse()
	drain()
	#low measuring
	low_measurement()
	drain()
	#high measuring
	high_measurement()
	drain()
	#sample measuring
	rinse_using_sample()
	drain()
	sample_measurement()
	##high measuring
	##drain()
	##high_measurement()
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
