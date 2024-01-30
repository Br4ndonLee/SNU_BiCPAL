import os, sys
import serial
import time
import string, struct
import csv
import datetime
import schedule
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
GPIO.setup(32, GPIO.OUT)
# GPIO.setup(36, GPIO.OUT)
# GPIO.setup(38, GPIO.OUT)
# GPIO.setup(40, GPIO.OUT)
pwm = GPIO.PWM(32, 100)
pwm.start(100)

now = datetime.datetime.now()

#f = open(str(now)+'env.csv','a', newline='')
#wr = csv.writer(f)

ser = serial.Serial('/dev/ttyUSB0',9600, timeout = 10)

def run():
    while True:
        #ser.write(bytes(bytearray([0x03,0x01,0x52,0x00,0x00,0x00,0x31,0x86,0x0D,0x0A])))
        #print("start")
        line = ser.read(24)
        #print('a')
        if len(line) == 0:
            print("no data")
            break;
        hex_list = ["{:x}".format(c) for c in line]
        o2 = hex_list[3:7]          #slicing
        temperature = hex_list[8:13]
        humidity = hex_list[14:18]
    
        o2_str = str(o2)                 #hex to string
        temp_str = str(temperature)
        humi_str = str(humidity)
#   print temperature[0]    
    #   print ' '.join(hex_list)
    #   print "O2 value is : %s%s%s%s ppm " %(o2_str[3], o2_str[9], o2_str[15],o2_str[21])
    #   print "Current temperature is : %s%s.%s C*" %(temp_str[9], temp_str[15], temp_str[26])
    #   print "Current humidity value is : %s%s.%s %s " %(humi_str[3], humi_str[9], humi_str[21], "%")
    #   print "%s%s.%s" %(temp_str[9], temp_str[15], temp_str[26])
    #   print "%s%s%s%s" %(o2_str[3], o2_str[9], o2_str[15],o2_str[21])
    #   print "%s%s.%s" %(humi_str[3], humi_str[9], humi_str[21])
        global a
        global c
        global d
        if temperature[0] == '20':
             a = humi_str[3]+humi_str[9]+"."+humi_str[21]
             c = temp_str[9]+temp_str[15]+"."+temp_str[27]
             d = o2_str[3]+o2_str[9]+o2_str[15]+o2_str[21]
#   print a.zfill(5)+" "+c.zfill(5)+" "+d.zfill(5) 
        else: 
             a = humi_str[3]+humi_str[9]+"."+humi_str[21]
             c = "-"+temp_str[9]+temp_str[15]+"."+temp_str[27]
             d = o2_str[3]+o2_str[9]+o2_str[15]+o2_str[21]
        global hum_int
        global co2_int
        global temp_int

        hum_int = float(a)
        co2_int = float(d)
        temp_int = float(c)
        
        if  (hum_int > 2 and co2_int < 3000) and temp_int < 60:
            print(a.zfill(5)+" "+c.zfill(5)+" "+d.zfill(5))
            now = datetime.datetime.now()
            wr.writerow([now, c, a, d])
            #print("chk",[now,c,a,d])
            #print(hum_int, co2_int, temp_int)
            f.flush()
            break
            #f.close()
        else:
            print("                                           ")     
    #   print type(a)
    #   print type(b)

def job():
    now = datetime.datetime.now()
    global f
    global wr
    f = open(str(now)+'env.csv','a', newline='')
    wr = csv.writer(f)

    try:
        while True:
            time.sleep(60)
            run()
            
            print("temp = ", temp_int, "humi = ", hum_int)
            
    except KeyboardInterrupt:
            GPIO.cleanup()
            f.close()
    #f.close()

#schedule.every().day.at("04:10").do(job)
#while True:
#    schedule.run_pending()
#    time.sleep(1)
#pwm.stop()
#GPIO.output(40, GPIO.HIGH)
    #break;
    

job()
