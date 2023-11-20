import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
# pump 1
GPIO.setup(21,GPIO.OUT)
# pump 2
GPIO.setup(22,GPIO.OUT)
# pump 3
GPIO.setup(23,GPIO.OUT)
# volumetric pump 1
GPIO.setup(24,GPIO.OUT)
# volumetric pump 2
GPIO.setup(25,GPIO.OUT)

print("setup")
time.sleep(2)

for i in range(1,3):
    GPIO.output(21,True)
    print("Pump 1 true")
    time.sleep(2)

    GPIO.output(22,True)
    print("Pump 2 true")
    time.sleep(2)
    
    GPIO.output(23,True)
    print("Pump 3 true")
    time.sleep(2)
    
    GPIO.output(24,True)
    print("Vol_Pump 1 true")
    time.sleep(2)

    GPIO.output(25,True)
    print("Vol_Pump 2 true")
    time.sleep(2)

    GPIO.output(21,False)
    print("Pump 1 false")
    time.sleep(2)

    GPIO.output(22,False)
    print("Pump 2 false")
    time.sleep(2)
    
    GPIO.output(23,False)
    print("Pump 3 false")
    time.sleep(2)
    
    GPIO.output(24,False)
    print("Vol_Pump 1 false")
    time.sleep(2)

    GPIO.output(25,False)
    print("Vol_Pump 2 false")
    time.sleep(2)

GPIO.cleanup()
print("cleanup")
time.sleep(2)