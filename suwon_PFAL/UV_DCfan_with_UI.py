import RPi.GPIO as GPIO
import time
from datetime import datetime
import threading
import tkinter as tk

class UVController:
    def __init__(self, uv_pin, status_callback):
        self.uv_pin = uv_pin
        GPIO.setup(self.uv_pin, GPIO.OUT)
        self.uv_on = False
        self.status_callback = status_callback

    def toggle_uv(self, state):
        if state:
            GPIO.output(self.uv_pin, False)
            self.status_callback("UV ON")
        else:
            GPIO.output(self.uv_pin, True)
            self.status_callback("UV OFF")

    def run(self):
        try:
            while True:
                now = datetime.now()
                hour = now.hour

                if hour >= 20 and hour < 22:
                    if not self.uv_on:
                        self.toggle_uv(True)
                        self.uv_on = True
                else:
                    if self.uv_on:
                        self.toggle_uv(False)
                        self.uv_on = False

                time.sleep(10)
        except KeyboardInterrupt:
            GPIO.cleanup()

class FanController:
    def __init__(self, right_fan_pin, left_fan_pin, status_callback):
        self.right_fan_pin = right_fan_pin
        self.left_fan_pin = left_fan_pin
        GPIO.setup(self.right_fan_pin, GPIO.OUT)
        GPIO.setup(self.left_fan_pin, GPIO.OUT)
        self.status_callback = status_callback
        self.fans_on = False

    def toggle_fans(self, state):
        if state:
            GPIO.output(self.right_fan_pin, False)
            GPIO.output(self.left_fan_pin, False)
            self.status_callback("Fans On")
        else:
            GPIO.output(self.right_fan_pin, True)
            GPIO.output(self.left_fan_pin, True)
            self.status_callback("Fans Off")

    def run(self):
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            GPIO.cleanup()

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("UV and Fan Controller")
        self.geometry("500x200")

        self.status_label_uv = tk.Label(self, text="UV Status: -", font=("Helvetica", 14))
        self.status_label_uv.pack(pady=10)

        self.status_label_fans = tk.Label(self, text="Fans Status: -", font=("Helvetica", 14))
        self.status_label_fans.pack(pady=10)

        self.uv_controller = UVController(uv_pin=4, status_callback=self.update_status_uv)
        self.fan_controller = FanController(right_fan_pin=22, left_fan_pin=24, status_callback=self.update_status_fans)

        uv_thread = threading.Thread(target=self.uv_controller.run)
        fan_thread = threading.Thread(target=self.fan_controller.run)

        uv_thread.start()
        fan_thread.start()

        self.create_controls()

    def create_controls(self):
        uv_button = tk.Button(self, text="Toggle UV", command=self.toggle_uv)
        uv_button.pack()

        fans_button = tk.Button(self, text="Toggle Fans", command=self.toggle_fans)
        fans_button.pack()

    def toggle_uv(self):
        self.uv_controller.toggle_uv(not self.uv_controller.uv_on)
        self.uv_controller.uv_on = not self.uv_controller.uv_on

    def toggle_fans(self):
        self.fan_controller.toggle_fans(not self.fan_controller.fans_on)
        self.fan_controller.fans_on = not self.fan_controller.fans_on

    def update_status_uv(self, message):
        self.status_label_uv.config(text="UV Status: " + message)

    def update_status_fans(self, message):
        self.status_label_fans.config(text="Fans Status: " + message)

if __name__ == "__main__":
    GPIO.setmode(GPIO.BCM)
    app = App()
    app.mainloop()
    GPIO.cleanup()
