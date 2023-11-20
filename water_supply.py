import RPi.GPIO as GPIO
import time
import datetime
import math
import atexit # exit alert
import os
import numpy as np
import serial

#### serial setting
#serial using arduino due
com = serial.Serial(port = "/dev/ttyACM0",
                    baudrate=9600,
                    bytesize = serial.EIGHTBITS,
                    parity = serial.PARITY_NONE,
                    timeout = 1)

def handle_exit():
    print("exit")

def get_EC(val):
    line = 0
    com.write(b'a')
    if com.in_waiting > 0:
        line = com.readline().decode('utf-8')
        line = float(line)
        print("ec received:", line)
    return line

def get_pH(val):
    line = 0
    com.write(b'b')
    if com.in_waiting > 0:
        line = com.readline().decode('utf-8')
        line = float(line)
        print("pH received:", line)
    return line

#### handle_exit
atexit.register(handle_exit)

#### GPIO setting
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
#relay number for pump
GPIO.setup(16, GPIO.OUT)
GPIO.setup(18, GPIO.OUT)
GPIO.setup(29, GPIO.OUT)

#relay number
GPIO.setup(31, GPIO.OUT)
GPIO.setup(32, GPIO.OUT)
GPIO.setup(33, GPIO.OUT)
GPIO.setup(35, GPIO.OUT)
GPIO.setup(36, GPIO.OUT)
GPIO.setup(37, GPIO.OUT)
GPIO.setup(38, GPIO.OUT)
GPIO.setup(40, GPIO.OUT)

# variable
ec = 0.85
ph = 6.9
bed_full_volume = 20 #litter
flow_rate_supply = 23/85 # litter per second
flow_rate_supply = 30/100
supplying_time = bed_full_volume/flow_rate_supply
supplying_time = 80
#0.2076 #96.34
ref_irr = 110

try:
    print("drainage start...")
    GPIO.output(16, GPIO.LOW) # pump on #relay ch2 # drainage pump
    dstart = time.time()
    print(dstart)
    while True:
        if (time.time() - dstart) > 345: #145
            print(time.time())
            break
    #time.sleep (35)
    GPIO.output(16, GPIO.HIGH)
    print("drainage stop")
    #print("initial ec:", get_EC(ec))
    #print("initial ph:", get_pH(ph))
    print("supplying and irrigation start simultaneously")
    GPIO.output(18, GPIO.LOW) # pump on #relay ch3 # supplying pump
    GPIO.output(29, GPIO.LOW) # pump on #relay ch4 # irrigation pump
    for i in range(0,supplying_time):
        ec = get_EC(ec)
        if i%2 == 0:
            if ec < 1.5:
                GPIO.output(31, GPIO.HIGH)
                GPIO.output(32, GPIO.HIGH)
                GPIO.output(33, GPIO.HIGH)
                GPIO.output(35, GPIO.HIGH)
                GPIO.output(36, GPIO.HIGH)
                GPIO.output(37, GPIO.HIGH)
                GPIO.output(38, GPIO.HIGH)
                GPIO.output(40, GPIO.HIGH)
        else:
            GPIO.output(31, GPIO.LOW)
            GPIO.output(32, GPIO.LOW)
            GPIO.output(33, GPIO.LOW)
            GPIO.output(35, GPIO.LOW)
            GPIO.output(36, GPIO.LOW)
            GPIO.output(37, GPIO.LOW)
            GPIO.output(38, GPIO.LOW)
            GPIO.output(40, GPIO.LOW)
        time.sleep(1)
    #time.sleep (supplying_time)
    print("supplying stop")
    GPIO.output(31, GPIO.LOW)
    GPIO.output(32, GPIO.LOW)
    GPIO.output(33, GPIO.LOW)
    GPIO.output(35, GPIO.LOW)
    GPIO.output(36, GPIO.LOW)
    GPIO.output(37, GPIO.LOW)
    GPIO.output(38, GPIO.LOW)
    GPIO.output(40, GPIO.LOW)
    GPIO.output(18, GPIO.HIGH)
    #print("after supplying ec:", get_EC(ec))
    #print("after supplying ph:", get_pH(ph))

    irr_time = ref_irr-supplying_time
    for i in range(0,irr_time):
        ec = get_EC(ec)
        if i%2 == 0:
            if ec < 1.5:
                GPIO.output(31, GPIO.HIGH)
                GPIO.output(32, GPIO.HIGH)
                GPIO.output(33, GPIO.HIGH)
                GPIO.output(35, GPIO.HIGH)
                GPIO.output(36, GPIO.HIGH)
                GPIO.output(37, GPIO.HIGH)
                GPIO.output(38, GPIO.HIGH)
                GPIO.output(40, GPIO.HIGH)
        else:
            GPIO.output(31, GPIO.LOW)
            GPIO.output(32, GPIO.LOW)
            GPIO.output(33, GPIO.LOW)
            GPIO.output(35, GPIO.LOW)
            GPIO.output(36, GPIO.LOW)
            GPIO.output(37, GPIO.LOW)
            GPIO.output(38, GPIO.LOW)
            GPIO.output(40, GPIO.LOW)
        time.sleep(1)

    #istart = time.time()
    #time.sleep(110-supplying_time)
    print("irrigation stop")
    GPIO.output(31, GPIO.LOW)
    GPIO.output(32, GPIO.LOW)
    GPIO.output(33, GPIO.LOW)
    GPIO.output(35, GPIO.LOW)
    GPIO.output(36, GPIO.LOW)
    GPIO.output(37, GPIO.LOW)
    GPIO.output(38, GPIO.LOW)
    GPIO.output(40, GPIO.LOW)
    GPIO.output(29, GPIO.HIGH)
    #print("final ec:", get_EC(ec))
    #print("final ph:", get_pH(ph))
    time.sleep(3)
    GPIO.output(16, GPIO.HIGH)
    GPIO.output(18, GPIO.HIGH)

except Exception as e:
    GPIO.output(16, GPIO.HIGH)
    GPIO.output(18, GPIO.HIGH)
    GPIO.output(29, GPIO.HIGH)
    GPIO.output(31, GPIO.LOW)
    GPIO.output(32, GPIO.LOW)
    GPIO.output(33, GPIO.LOW)
    GPIO.output(35, GPIO.LOW)
    GPIO.output(36, GPIO.LOW)
    GPIO.output(37, GPIO.LOW)
    GPIO.output(38, GPIO.LOW)
    GPIO.output(40, GPIO.LOW)
    print("error")

except KeyboardInterrupt:
    GPIO.output(16, GPIO.HIGH)
    GPIO.output(18, GPIO.HIGH)
    GPIO.output(29, GPIO.HIGH)
    GPIO.output(31, GPIO.LOW)  
    GPIO.output(32, GPIO.LOW)
    GPIO.output(33, GPIO.LOW)
    GPIO.output(35, GPIO.LOW)
    GPIO.output(36, GPIO.LOW)
    GPIO.output(37, GPIO.LOW)
    GPIO.output(38, GPIO.LOW)
    GPIO.output(40, GPIO.LOW)
