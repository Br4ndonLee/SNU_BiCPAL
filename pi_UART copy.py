#!/usr/bin/env python3
import serial
import time
import RPi.GPIO as GPIO

# for loopback test, open virtual file ttyAMA0(ttyS0)
if(GPIO.RPI_REVISION < 3):
    ser = serial.Serial(port = "/dev/ttyAMA0", baudrate=9600, timeout = 2)
else:
    ser = serial.Serial(port = "/dev/ttyS0", baudrate=9600, timeout = 2)

if (ser.isOpen() == False):
    ser.open()
    
# if the data left in ttyAMA0, delete and start again
ser.flushInput()
ser.flushOutput()

ch_num = 0

b1 = bytes([ch_num])
packet = b1

ser.flushInput()
ser.flushOutput()

# send the packet
ser.write(packet)
print("Send:", packet)

##############
# Define main task
##############
def echotest():
    while(True):
        if ser.readable():
            break
            time.sleep(0.01)

        # read the packet come from loopback again
        data = ser.readline
        print ("Receive:", data)

################
# Define DESTROY Function
###############
def destroy():
    ser.close ()
    print ("TEST COMPLETE!")

#################
# Main Program
#################
if __name__ == '__main__':
    try:
        echotest()
    except KeyboardInterrupt:
        destroy ()
    finally:
        destroy()