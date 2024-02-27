import time
import spidev
# import tkinter as tk
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(5, GPIO.OUT)
GPIO.setup(6, GPIO.OUT)
GPIO.setup(13, GPIO.OUT)
GPIO.setup(19, GPIO.OUT)
GPIO.setup(26, GPIO.OUT)


class ECpHMonitor:
    def __init__(self):
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 1000000
        self.repeat_count = 10000
        self.channels = [0, 1, 2, 3, 4, 5, 6, 7]

    def read_channel(self, channel):
        r = self.spi.xfer2([6 | (channel >> 2), channel << 6, 0])
        adc_out = ((r[1] & 15) << 8) + r[2]
        return adc_out

    def read_and_average(self, channel):
        readings = []
        repeat = 0

        while repeat < self.repeat_count:
            repeat += 1
            inp = self.read_channel(channel)
            voltage = inp * 3.3 / 4095
            round_inp = round(voltage, 3)
            readings.append(round_inp)

        return sum(readings, 0.0) / len(readings)

    def measure_EC_pH_value(self, channel):
        return self.read_and_average(channel)

    def EC_pH_calculate(self):
        pH_val = 6.1098 * self.measure_EC_pH_value(1) - 5.236
        ec_val = 3.8409 * self.measure_EC_pH_value(2) - 3.4449
        return pH_val, ec_val

    def cleanup(self):
        GPIO.cleanup()
        self.f.close()

    def pump_control(self):
        pH_val, ec_val = self.EC_pH_calculate()
        print("pH : ", pH_val, "EC : ", ec_val)

        # pump for EC control
        if ec_val < 1.5:
            GPIO.output(5, False)
            GPIO.output(6, False)
            print("Activated pumps for EC")
            while ec_val >= 1.5:
                print("EC : ", ec_val)
                time.sleep(1)
                ec_val = self.measure_EC_pH_value(2)

            # GPIO.output(5, True)
            # GPIO.output(6, True)
            # print("Deactivated pumps for EC")
        else:
            GPIO.output(5, True)
            GPIO.output(6, True)
            print("Deactivated pumps for EC")
            

        # pump for pH
        if pH_val > 7.5:
            GPIO.output(13, False)
            print("Activated pumps for pH")
            while pH_val <= 6.5:
                print("pH : ", pH_val)
                time.sleep(1)
                pH_val = self.measure_EC_pH_value(1)

            # GPIO.output(13, True)
            # print("Deactivated pumps for pH")
        else:
            GPIO.output(13, True)
            print("Deactivated pumps for pH")


if __name__ == "__main__":
    try:
        ec_ph_monitor = ECpHMonitor()
        while True:
            ec_ph_monitor.pump_control()

    except KeyboardInterrupt:
        ec_ph_monitor.cleanup()
