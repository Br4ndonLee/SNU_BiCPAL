import RPi.GPIO as GPIO
from datetime import datetime
import tkinter as tk
import pause

GPIO.setmode(GPIO.BCM)

GPIO.setup(23, GPIO.OUT)
# volumetric pump 1
GPIO.setup(24, GPIO.OUT)

def update_status():
    now = datetime.now()
    hour = now.hour
    minute = now.minute
    if 6 <= hour <= 23:
        GPIO.output(23, False)
        GPIO.output(24, False)
        status_label.config(text="LED ON\nCurrent Time: {}:{}" .format(hour, minute))
    else:
        GPIO.output(23, True)
        GPIO.output(24, True)
        status_label.config(text="LED OFF\nCurrent Time: {}:{}" .format(hour, minute))

def turn_on_led_for_five_minutes():
    GPIO.output(23, False)
    GPIO.output(24, False)
    status_label.config(text="LED ON for 5 minutes")

    pause.minutes(5)
    
    turn_off_led()

def turn_off_led():
    GPIO.output(23, True)
    GPIO.output(24, True)
    status_label.config(text="LED OFF")

def update_status_periodically():
    update_status()
    root.after(5000, update_status_periodically)  # 5000 milliseconds (5 seconds)

try:
    root = tk.Tk()
    root.title("LED Status")
    root.geometry("400x200")  # 윈도우 크기 설정

    status_label = tk.Label(root, text="", font=("Helvetica", 16))
    status_label.pack(pady=20)

    on_button = tk.Button(root, text="Turn On LED for 5 minutes", command=turn_on_led_for_five_minutes)
    on_button.pack(pady=10)

    update_status_periodically()

    root.mainloop()

except KeyboardInterrupt:
    GPIO.cleanup()
    print("END")
