import time
import spidev
import datetime
import pandas as pd

class WaterLevelMonitor:
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

    def measure_water_level(self, channel):
        return self.read_and_average(channel)

    def run(self):
        while True:
            left_lv = 13.602 * self.measure_water_level(0) - 8.108
            right_lv = 13.18 * self.measure_water_level(1) - 8.0568

            print("Left:", left_lv, "cm, ", self.measure_water_level(0), "mV")
            print("Right:", right_lv, "cm, ", self.measure_water_level(1), "mV")

            # Add any additional processing or output as needed
            time.sleep(1)  # Adjust sleep duration as needed

if __name__ == "__main__":
    water_level_monitor = WaterLevelMonitor()
    water_level_monitor.run()