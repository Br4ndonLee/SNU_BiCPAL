"""CH8.ipynb
2022.3.3
Multiple Water Source Ion Balance Management System
Dosing Algorithm - JooShin Kim
"""
import csv
import datetime as dt
from multiprocessing import Process
import RPi.GPIO as p
import time
import serial
import math
import sys
from datetime import datetime
import spidev


now = dt.datetime.now()
nowDatetime = now.strftime('%Y-%m-%d %H:%M') ##:%S second can be added
spi = spidev.SpiDev()
spi.open(0, 1)
spi.max_speed_hz = 1000000

##############Supply Water Predicted Concentration####################
Predicted_Calcium = 0
Predicted_Nitrate = 0
Predicted_Potassium = 0
############################################
Na_final_value = 0
Efflu_Na_final_value = 0
rain_Na_final_value = 0
under_Na_final_value = 0

repeat = 0
no3_s = []       #nutrient
Na_low = []
no3_high = []
under_water = []
effluent = []
rainy = []
##############################################################<------------------
#LOW_Na1 = 0.0111 * math.log10(13.74) * 2.302585093 + 0.9802
#HIGH_Na1 = 0.0111 * math.log10(125.45) * 2.302585093 + 0.9802
LOW_Na1 = 0.014 * math.log10(8.40) * 2.302585093 + 0.9968
HIGH_Na1 = 0.014 * math.log10(142.6) * 2.302585093 + 0.9968
LOW_Na2 = 0.014 * math.log10(8.40) * 2.302585093 + 0.9968
HIGH_Na2 = 0.014 * math.log10(142.6) * 2.302585093 + 0.9968
LOW_Na3 = 0.014 * math.log10(8.40) * 2.302585093 + 0.9968
HIGH_Na3 = 0.014 * math.log10(142.6) * 2.302585093 + 0.9968
#######################GPIO_Setting############################


def ReadChannel3208(channel):
    r = spi.xfer2([6 | (channel >> 2), channel << 6, 0])
    adc_out = ((r[1] & 15) << 8) + r[2]
    return adc_out


def LOW(num):
    global repeat
    global Na_low
    Na_low = []
    while repeat < 1000:
        repeat = repeat + 1
        inpa = ReadChannel3208(num)
        Na_low.append(inpa)
        if repeat == 1000:
            Na_now = sum(Na_low, 0.0) / len(Na_low)
            globals()['Nay10{}'.format(num)] = Na_now * 3.3 / 4095
            #print('LOW{}: {}'.format(num, round(globals()['Nay10{}'.format(num)], 3)))
    repeat = 0


def HIGH(num):
    global repeat
    global no3_high
    no3_high = []
    while repeat < 1000:
        repeat = repeat + 1
        inpb = ReadChannel3208(num)
        no3_high.append(inpb)
        if repeat == 1000:
            no3_now = sum(no3_high, 0.0) / len(no3_high)
            globals()['Nay20{}'.format(num)] = no3_now * 3.3 / 4095
            #print('HIGH{}: {}'.format(num, round(globals()['Nay20{}'.format(num)], 3)))
    repeat = 0
    
    
def RAIN(num):
    global repeat
    global rainy
    rainy = []
    while repeat < 1000:
        repeat = repeat + 1
        inpura = ReadChannel3208(num)
        rainy.append(inpura)
        if repeat == 1000:
            ra3_now = sum(rainy, 0.0) / len(rainy)
            globals()['Rainyy{}'.format(num)] = ra3_now * 3.3 / 4095
            print('RainT{}: {}'.format(num, round(globals()['Rainyy{}'.format(num)], 3)))

            globals()['Rain_Comp{}'.format(num)] = (globals()['NaRatio{}'.format(num)]) * (globals()['Rainyy{}'.format(num)]) + (
            globals()['NaOffset{}'.format(num)])
            #print('Ratio{}: {}'.format(num, round(globals()['NaRatio{}'.format(num)], 3)))
            #print('Offset{}: {}'.format(num, round(globals()['NaOffset{}'.format(num)], 3)))
            #print('Compensation{}: {}'.format(num, round(globals()['Rain_Comp{}'.format(num)], 4)))
            
            #if num == 0:
            #    globals()['rain_result{}'.format(num)] = math.pow(10, ((globals()['Rain_Comp{}'.format(num)]) - 0.9802) / (
            #                0.0111 * 2.302585093))
            if num == 0:
                globals()['rain_result{}'.format(num)] = math.pow(10, ((globals()['Rain_Comp{}'.format(num)]) - 0.9968) / (
                            0.014 * 2.302585093))            
            elif num == 1:
                globals()['rain_result{}'.format(num)] = math.pow(10, ((globals()['Rain_Comp{}'.format(num)]) - 0.9968) / (
                            0.014 * 2.302585093))
            elif num == 2:
                globals()['rain_result{}'.format(num)] = math.pow(10, ((globals()['Rain_Comp{}'.format(num)]) - 0.9968) / (
                            0.014 * 2.302585093))   
                        
            #print('current rain PPM{}: {}'.format(num, round(globals()['rain_result{}'.format(num)], 2)))
            
    repeat = 0
    
def UNDERGROUND(num): #complete
    global repeat
    global under_water
    under_water = []
    while repeat < 1000:
        repeat = repeat + 1
        inpu = ReadChannel3208(num)
        under_water.append(inpu)
        if repeat == 1000:
            no3_now = sum(under_water, 0.0) / len(under_water)
            globals()['Under{}'.format(num)] = no3_now * 3.3 / 4095
            print('Underground{}: {}'.format(num, round(globals()['Under{}'.format(num)], 3)))
       
            globals()['Under_Comp{}'.format(num)] = (globals()['NaRatio{}'.format(num)]) * (globals()['Under{}'.format(num)]) + (
            globals()['NaOffset{}'.format(num)])
            
            #print('Ratio{}: {}'.format(num, round(globals()['NaRatio{}'.format(num)], 3)))
            #print('Offset{}: {}'.format(num, round(globals()['NaOffset{}'.format(num)], 3)))
            #print('Compensation{}: {}'.format(num, round(globals()['Under_Comp{}'.format(num)], 4)))
            
            #if num == 0:
            #    globals()['underground_result{}'.format(num)] = math.pow(10, ((globals()['Under_Comp{}'.format(num)]) - 0.9802) / (
            #                0.0111 * 2.302585093))
            if num == 0:
                globals()['underground_result{}'.format(num)] = math.pow(10, ((globals()['Under_Comp{}'.format(num)]) - 0.9968) / (
                            0.014 * 2.302585093))
            elif num == 1:
                globals()['underground_result{}'.format(num)] = math.pow(10, ((globals()['Under_Comp{}'.format(num)]) - 0.9968) / (
                            0.014 * 2.302585093))
            elif num == 2:
                globals()['underground_result{}'.format(num)] = math.pow(10, ((globals()['Under_Comp{}'.format(num)]) - 0.9968) / (
                            0.014 * 2.302585093))   

            #print('current under PPM{}: {}'.format(num, round(globals()['underground_result{}'.format(num)], 2)))
            
    repeat = 0

def EFFLUENT(num):
    global repeat
    global effluent
    effluent = []
    while repeat < 1000:
        repeat = repeat + 1
        inpua = ReadChannel3208(num)
        effluent.append(inpua)
        if repeat == 1000:
            ra32_now = sum(effluent, 0.0) / len(effluent)
            globals()['Efflu{}'.format(num)] = ra32_now * 3.3 / 4095
            print('Effulent{}: {}'.format(num, round(globals()['Efflu{}'.format(num)], 3)))
            
            globals()['Effluent_Comp{}'.format(num)] = (globals()['NaRatio{}'.format(num)]) * (globals()['Efflu{}'.format(num)]) + (
            globals()['NaOffset{}'.format(num)])
            #print('Ratio{}: {}'.format(num, round(globals()['NaRatio{}'.format(num)], 3)))
            #print('Offset{}: {}'.format(num, round(globals()['NaOffset{}'.format(num)], 3)))
            #print('Efflu Compensation{}: {}'.format(num, round(globals()['Effluent_Comp{}'.format(num)], 4)))
            
            if num == 0:
                globals()['Effluent_result{}'.format(num)] = math.pow(10, ((globals()['Effluent_Comp{}'.format(num)]) - 0.9802) / (
                            0.0111 * 2.302585093))
            elif num == 1:
                globals()['Effluent_result{}'.format(num)] = math.pow(10, ((globals()['Effluent_Comp{}'.format(num)]) - 0.9968) / (
                            0.014 * 2.302585093))
            elif num == 2:
                globals()['Effluent_result{}'.format(num)] = math.pow(10, ((globals()['Effluent_Comp{}'.format(num)]) - 0.9968) / (
                            0.014 * 2.302585093))

            #print('current Effluent PPM{}: {}'.format(num, round(globals()['Effluent_result{}'.format(num)], 2)))
            

    repeat = 0 

def NUTRIENT(num):
    global repeat
    global no3_s
    no3_s = []
    # sample measuring
    while repeat < 10000:
        repeat = repeat + 1
        inpc = ReadChannel3208(num)
        no3_s.append(inpc)
        if repeat == 10000:
            no12_now = sum(no3_s, 0.0) / len(no3_s)
            globals()['NaS{}'.format(num)] = no12_now * 3.3 / 4095
            #print('Nutrient{}: {}'.format(num, round(globals()['NaS{}'.format(num)], 3)))
            if num == 0:
                globals()['NaRatio{}'.format(num)] = (HIGH_Na1 - LOW_Na1) / (
                            globals()['Nay20{}'.format(num)] - globals()['Nay10{}'.format(num)])
                globals()['NaOffset{}'.format(num)] = HIGH_Na1 - (
                            (globals()['Nay20{}'.format(num)]) * (globals()['NaRatio{}'.format(num)])) 
            elif num == 1:  # NO1
                globals()['NaRatio{}'.format(num)] = (HIGH_Na2 - LOW_Na2) / (
                            globals()['Nay20{}'.format(num)] - globals()['Nay10{}'.format(num)])
                globals()['NaOffset{}'.format(num)] = HIGH_Na2 - (
                            (globals()['Nay20{}'.format(num)]) * (globals()['NaRatio{}'.format(num)]))
            elif num == 2:
                globals()['NaRatio{}'.format(num)] = (HIGH_Na3 - LOW_Na3) / (
                            globals()['Nay20{}'.format(num)] - globals()['Nay10{}'.format(num)])
                globals()['NaOffset{}'.format(num)] = HIGH_Na3 - (
                            (globals()['Nay20{}'.format(num)]) * (globals()['NaRatio{}'.format(num)]))   
            
            globals()['NA{}'.format(num)] = (globals()['NaRatio{}'.format(num)]) * (globals()['NaS{}'.format(num)]) + (
            globals()['NaOffset{}'.format(num)])

            #print('Ratio{}: {}'.format(num, round(globals()['NaRatio{}'.format(num)], 3)))
            #print('Offset{}: {}'.format(num, round(globals()['NaOffset{}'.format(num)], 3)))
            #print('Compensation{}: {}'.format(num, round(globals()['NA{}'.format(num)], 4)))

            #if num == 0:
            #    globals()['result{}'.format(num)] = math.pow(10, ((globals()['NA{}'.format(num)]) - 0.9802) / (
            #                0.0111 * 2.302585093))
            if num == 0:
                globals()['result{}'.format(num)] = math.pow(10, ((globals()['NA{}'.format(num)]) - 0.9968) / (
                            0.014 * 2.302585093))
            elif num == 1:
                globals()['result{}'.format(num)] = math.pow(10, ((globals()['NA{}'.format(num)]) - 0.9968) / (
                            0.014 * 2.302585093))
            elif num == 2:
                globals()['result{}'.format(num)] = math.pow(10, ((globals()['NA{}'.format(num)]) - 0.9968) / (
                            0.014 * 2.302585093))    
            

            #print('Mixing Tank PPM{}: {}'.format(num, round(globals()['result{}'.format(num)], 2)))

    repeat = 0
            
def calibration():
###################LOW#######################
    for i in range(3):
        LOW(i)

    for i in range(3):
        HIGH(i)

    for i in range(3):
        NUTRIENT(i)
############################################################################
    result_0 = round(result0,3); result_1 = round(result1,3); result_2 = round(result2,3)
##########Average ISE result shown here. This part must be modified to detect which ISE is availabe or which is not###########
    Na_value_select0 = (result_0 + result_1)/2
    Na_value_select1 = (result_1 + result_2)/2
    Na_value_select2 = (result_0 + result_2)/2
    Na_final_value = min(Na_value_select0, Na_value_select1, Na_value_select2)
  
#############Tank Water Status##############    
    #print("Target-Current:",Target_Current,"L")
    print("#####Predicted Value####")
    print("Na_1 : ", result_0,"mg/L")
    print("Na_2 : ", result_1,"mg/L")
    print("Na_3 : ", result_2,"mg/L")
    print("#####Final Predicted Value####")
    print("Sodium : ", Na_final_value)

    for i in range(3):
        RAIN(i)
    p_rain_0 = round(rain_result0,3); p_rain_1 = round(rain_result1,3); p_rain_2 = round(rain_result2,3)
                    
    rain_Na_value_select0 = (p_rain_0 + p_rain_1)/2
    rain_Na_value_select1 = (p_rain_1 + p_rain_2)/2
    rain_Na_value_select2 = (p_rain_0 + p_rain_2)/2
    rain_Na_final_value = min(rain_Na_value_select0, rain_Na_value_select1, rain_Na_value_select2)
            
        
    Rain_Predicted_Sodium = rain_Na_final_value        
    
    print("#####rain Predicted Value####")
    print("rain Na_1 : ", p_rain_0,"mg/L")
    print("rain Na_2 : ", p_rain_1,"mg/L")
    print("rain Na_3 : ", p_rain_2,"mg/L")
    print("#####rain Final Predicted Value####")
    print("rain Sodium : ", rain_Na_final_value)
    
    for i in range(3):
        UNDERGROUND(i)
    under_0 = round(Under0,3); under_1 = round(Under1,3); under_2 = round(Under2,3);
    p_under_0 = round(underground_result0,3)
    p_under_1 = round(underground_result1,3)
    p_under_2 = round(underground_result2,3)
##########Average ISE result shown here. This part must be modified to detect which ISE is availabe or which is not###########
    under_Na_value_select0 = (p_under_0 + p_under_1)/2
    under_Na_value_select1 = (p_under_1 + p_under_2)/2
    under_Na_value_select2 = (p_under_0 + p_under_2)/2
    under_Na_final_value = min(under_Na_value_select0, under_Na_value_select1, under_Na_value_select2)
         
    Under_Predicted_Sodium = under_Na_final_value
    print("#####under Predicted Value####")
    print("under Na_1 : ", p_under_0,"mg/L")
    print("under Na_2 : ", p_under_1,"mg/L")
    print("under Na_3 : ", p_under_2,"mg/L")
    print("#####under Final Predicted Value####")
    print("under Sodium : ", under_Na_final_value) 
       
#calibration()    
#water_height()    
#calibration()
#Ion_Replenishment()











