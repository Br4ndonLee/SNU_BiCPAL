import time
import spidev
import datetime
# import pandas as pd

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

if __name__ == "__main__":
    ec_ph_monitor = ECpHMonitor()

    
    while True:
        pH_val, ec_val = ec_ph_monitor.EC_pH_calculate()
        print("pH:", pH_val,", ", ec_ph_monitor.measure_EC_pH_value(1), "mV")
        print("EC:", ec_val, "mS/cm, ", ec_ph_monitor.measure_EC_pH_value(2), "mV")

        # Add any additional processing or output as needed
        time.sleep(1)  # Adjust sleep duration as needed