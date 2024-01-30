import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

# Right DC fan
GPIO.setup(22, GPIO.OUT)
# Left DC fan
GPIO.setup(24, GPIO.OUT)
print("Right DC fan On")
print("Left DC fan On")
try:
	while True:
		GPIO.output(22, False)
		# time.sleep(10)
		GPIO.output(24, False)		
		
except KeyboardInterrupt:
		GPIO.cleanup()
		f.close()
