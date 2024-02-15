import os
import sys
import serial
import string
import struct
import csv
import datetime
import schedule
import RPi.GPIO as GPIO
import pause

class SensorDataLogger:
    def __init__(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(32, GPIO.OUT)
        self.pwm = GPIO.PWM(32, 100)
        self.pwm.start(100)

        self.ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=10)

        self.f = None
        self.wr = None
        self.csv_file_path = "/home/pw0000/Desktop/Code/Temp_CSV/"

    def setup_csv_file(self):
        now = datetime.datetime.now()
        file_name = str(now) + 'env.csv'
        file_path = os.path.join(self.csv_file_path, file_name)
        self.f = open(file_path, 'a', newline='')
        self.wr = csv.writer(self.f)

    def cleanup(self):
        GPIO.cleanup()
        if self.f:
            self.f.close()

    def run(self):
        while True:
            line = self.ser.read(24)
            if len(line) == 0:
                print("no data")
                break

            hex_list = ["{:x}".format(c) for c in line]
            o2 = hex_list[3:7]
            temperature = hex_list[8:13]
            humidity = hex_list[14:18]

            o2_str = str(o2)
            temp_str = str(temperature)
            humi_str = str(humidity)

            global a, c, d
            if temperature[0] == '20':
                a = humi_str[3] + humi_str[9] + "." + humi_str[21]
                c = temp_str[9] + temp_str[15] + "." + temp_str[27]
                d = o2_str[3] + o2_str[9] + o2_str[15] + o2_str[21]
            else:
                a = humi_str[3] + humi_str[9] + "." + humi_str[21]
                c = "-" + temp_str[9] + temp_str[15] + "." + temp_str[27]
                d = o2_str[3] + o2_str[9] + o2_str[15] + o2_str[21]

            global hum_int, co2_int, temp_int
            hum_int = float(a)
            co2_int = float(d)
            temp_int = float(c)

            if (hum_int > 2 and co2_int < 3000) and temp_int < 60:
                print(a.zfill(5) + " " + c.zfill(5) + " " + d.zfill(5))
                now = datetime.datetime.now()
                self.wr.writerow([now, c, a, d])
                self.f.flush()
                break
            else:
                print("                                           ")

if __name__ == "__main__":
    sensor_logger = SensorDataLogger()
    sensor_logger.setup_csv_file()

    try:
        while True:
            pause.seconds(60)
            sensor_logger.run()
            print("temp = ", temp_int, "humi = ", hum_int)

    except KeyboardInterrupt:
        sensor_logger.cleanup()
