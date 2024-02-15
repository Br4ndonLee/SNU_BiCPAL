import time
import spidev
import datetime
# pandas for save to CSV file. if you don't need, you can delete
# import pandas as pd

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1000000
# def ReadChannel3008(channel):

start_time = datetime.datetime.now()
second_to_run = 2
data = []

# repeat0 = 0
repeat1 = 0
repeat2 = 0
repeat3 = 0
repeat4 = 0


def ReadChannel310008(channel):
    r=spi.xfer2([6 | (channel>>2), channel<<6,0])
    adc_out=((r[1]&15)<<8)+r[2]
    return adc_out      
       

# ch0=[]
ch1=[]
ch2=[]
ch3=[]
ch4 = []

        
def ch01():
    global repeat1
    global ch1
    ch1=[]
    repeat1 = 0
    while repeat1 < 10000 :
        repeat1 = repeat1 + 1
        inp1=ReadChannel310008(1)
        voltage1 = inp1*3.3/4095
        round_inp1 = round(voltage1, 3)
        #print (round_inpa)
        ch1.append(round_inp1)
       
        if repeat1 == 10000:
            ch1_now = sum(ch1, 0.0)/len(ch1)
            round_ch1=round(ch1_now,3)
            return round_ch1
        
def ch02():
    global repeat2
    global ch2
    ch2=[]
    repeat2 = 0
    while repeat2 < 10000 :
        repeat2 = repeat2 + 1
        inp2=ReadChannel310008(2)
        voltage2 = inp2*3.3/4095
        round_inp2 = round(voltage2, 3)
        #print (round_inpa)
        ch2.append(round_inp2)
       
        if repeat2 == 10000:
            ch2_now = sum(ch2, 0.0)/len(ch2)
            round_ch2=round(ch2_now,3)
            return round_ch2
        
def ch03():
    global repeat3
    global ch3
    ch3=[]
    repeat3 = 0
    while repeat3 < 10000 :
        repeat3 = repeat3 + 1
        inp3=ReadChannel310008(3)
        voltage3 = inp3*3.3/4095
        round_inp3 = round(voltage3, 3)
        #print (round_inpa)
        ch3.append(round_inp3)
       
        if repeat3 == 10000:
            ch3_now = sum(ch3, 0.0)/len(ch3)
            round_ch3=round(ch3_now,3)
            return round_ch3
        
        
def ch04():
    global repeat4
    global ch4
    ch4=[]
    repeat4 = 0
    while repeat4 < 1000 :
        repeat4 = repeat4 + 1
        inp4=ReadChannel310008(4)
        
        voltage4 = inp4*3.3/4095
        round_inp4 = round(voltage4, 3)
        #print (round_inpa)
        ch4.append(round_inp4)
        
        if repeat4 == 1000:
            ch4_now = sum(ch4, 0.0)/len(ch4)
            round_ch4=round(ch4_now,3)
            return round_ch4
        
       
while True:

    Channel1 = ch01()
    Channel2 = ch02()
    Channel3 = ch03()
    Channel4 = ch04()

    pH = 6.1098 * Channel1 - 5.236
    ec_1 = 3.8409 * Channel2 - 3.4449
    

    print("pH :", pH, "EC :", ec_1)

