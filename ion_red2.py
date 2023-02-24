"""CH8.ipynb
2022.6.3
Ion Monitoring System For GyungGiDOWON
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
import K_Sodium_Prediction as Sodium


now = dt.datetime.now()
nowDatetime = now.strftime('%Y-%m-%d %H:%M') ##:%S second can be added
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1000000


##################### GLOBAL ###############################
repeat = 0
no3_s = []       #nutrient
Na_low = []
no3_high = []
under_water = []
effluent = []
rainy = []
##############################################################<------------------
#LOW_NO1 = -0.018 * math.log10(21.8) * 2.302585093 + 0.8406
#HIGH_NO1 = -0.018 * math.log10(712.0) * 2.302585093 + 0.8406
LOW_NO1 = -0.02 * math.log10(21.8) * 2.302585093 + 1.2392
HIGH_NO1 = -0.02 * math.log10(712.0) * 2.302585093 + 1.2392
LOW_NO2 = -0.02 * math.log10(21.8) * 2.302585093 + 1.2392
HIGH_NO2 = -0.02 * math.log10(712.0) * 2.302585093 + 1.2392
#LOW_NO3 = -0.02 * math.log10(21.8) * 2.302585093 + 1.2392
#HIGH_NO3 = -0.02 * math.log10(712.0) * 2.302585093 + 1.2392
LOW_NO3 = -0.02 * math.log10(21.8) * 2.302585093 + 1.2277
HIGH_NO3 = -0.02 * math.log10(712.0) * 2.302585093 + 1.2277

#LOW_K1 = -0.02 * math.log10(6.07) * 2.302585093 + 1.1404
#HIGH_K1 = -0.02 * math.log10(220.03) * 2.302585093 + 1.1404
LOW_K1 = 0.015 * math.log10(6.07) * 2.302585093 + 0.9811
HIGH_K1 = 0.015 * math.log10(220.03) * 2.302585093 + 0.9811
LOW_K2 = 0.015 * math.log10(6.07) * 2.302585093 + 0.9811
HIGH_K2 = 0.015 * math.log10(220.03) * 2.302585093 + 0.9811
#LOW_K3 = -0.015 * math.log10(6.07) * 2.302585093 + 0.9811
#HIGH_K3 = -0.015 * math.log10(220.03) * 2.302585093 + 0.9811
LOW_K3 = 0.0165 * math.log10(6.07) * 2.302585093 + 1.0068
HIGH_K3 = 0.0165 * math.log10(220.03) * 2.302585093 + 1.0068

#LOW_Na1 = 0.0111 * math.log10(8.40) * 2.302585093 + 0.9802
#HIGH_Na1 = 0.0111 * math.log10(142.6) * 2.302585093 + 0.9802
LOW_Na1 = 0.014 * math.log10(8.40) * 2.302585093 + 0.9968
HIGH_Na1 = 0.014 * math.log10(142.6) * 2.302585093 + 0.9968
LOW_Na2 = 0.014 * math.log10(8.40) * 2.302585093 + 0.9968
HIGH_Na2 = 0.014 * math.log10(142.6) * 2.302585093 + 0.9968
LOW_Na3 = 0.014 * math.log10(8.40) * 2.302585093 + 0.9968
HIGH_Na3 = 0.014 * math.log10(142.6) * 2.302585093 + 0.9968

LOW_Ca1 = -0.016 * math.log10(21.8) * 2.302585093 + 1.6711
HIGH_Ca1 = -0.016 * math.log10(220.03) * 2.302585093 + 1.6711
LOW_Ca2 = -0.016 * math.log10(21.8) * 2.302585093 + 1.6711
HIGH_Ca2 = -0.016 * math.log10(220.03) * 2.302585093 + 1.6711
#######################GPIO_Setting############################
p.setmode(p.BCM)
p.setup([18, 17, 14, 15], p.OUT, initial=p.HIGH) #Dosing Unit
              #Chamber Unit  

def ReadChannel3208(channel): #MCP3298 ADC converter와 통신하기 위한 코드
    r = spi.xfer2([6 | (channel >> 2), channel << 6, 0])
    adc_out = ((r[1] & 15) << 8) + r[2]
    return adc_out


def LOW(num):               ### LOW 용액 전압 측정 코드
    global repeat
    global Na_low
    Na_low = []
    while repeat < 10000:
        repeat = repeat + 1
        inpa = ReadChannel3208(num)
        Na_low.append(inpa)
        if repeat == 10000:
            Na_now = sum(Na_low, 0.0) / len(Na_low)
            globals()['Nay10{}'.format(num)] = Na_now * 3.3 / 4095
            #print('LOW{}: {}'.format(num, round(globals()['Nay10{}'.format(num)], 3)))
    repeat = 0


def HIGH(num):           ### HIGH 용액 전압 측정 코드
    global repeat
    global no3_high
    no3_high = []
    while repeat < 10000:
        repeat = repeat + 1
        inpb = ReadChannel3208(num)
        no3_high.append(inpb)
        if repeat == 10000:
            no3_now = sum(no3_high, 0.0) / len(no3_high)
            globals()['Nay20{}'.format(num)] = no3_now * 3.3 / 4095
            #print('HIGH{}: {}'.format(num, round(globals()['Nay20{}'.format(num)], 3)))
    repeat = 0
    
def NUTRIENT(num):    # 양액 혼합 탱크 전압 측정 및 보상 코드 
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

            if num == 2:  # NO1
                globals()['NaRatio{}'.format(num)] = (HIGH_NO1 - LOW_NO1) / (
                            globals()['Nay20{}'.format(num)] - globals()['Nay10{}'.format(num)])
                globals()['NaOffset{}'.format(num)] = HIGH_NO1 - (
                            (globals()['Nay20{}'.format(num)]) * (globals()['NaRatio{}'.format(num)]))
            elif num == 3:
                globals()['NaRatio{}'.format(num)] = (HIGH_NO2 - LOW_NO2) / (
                            globals()['Nay20{}'.format(num)] - globals()['Nay10{}'.format(num)])
                globals()['NaOffset{}'.format(num)] = HIGH_NO2 - (
                            (globals()['Nay20{}'.format(num)]) * (globals()['NaRatio{}'.format(num)]))
            elif num == 4:
                globals()['NaRatio{}'.format(num)] = (HIGH_NO3 - LOW_NO3) / (
                            globals()['Nay20{}'.format(num)] - globals()['Nay10{}'.format(num)])
                globals()['NaOffset{}'.format(num)] = HIGH_NO3 - (
                            (globals()['Nay20{}'.format(num)]) * (globals()['NaRatio{}'.format(num)]))    
            elif num == 5:
                globals()['NaRatio{}'.format(num)] = (HIGH_K1 - LOW_K1) / (
                            globals()['Nay20{}'.format(num)] - globals()['Nay10{}'.format(num)])
                globals()['NaOffset{}'.format(num)] = HIGH_K1 - (
                            (globals()['Nay20{}'.format(num)]) * (globals()['NaRatio{}'.format(num)]))
            elif num == 6:
                globals()['NaRatio{}'.format(num)] = (HIGH_K2 - LOW_K2) / (
                            globals()['Nay20{}'.format(num)] - globals()['Nay10{}'.format(num)])
                globals()['NaOffset{}'.format(num)] = HIGH_K2 - (
                            (globals()['Nay20{}'.format(num)]) * (globals()['NaRatio{}'.format(num)]))
            elif num == 7:
                globals()['NaRatio{}'.format(num)] = (HIGH_K3 - LOW_K3) / (
                            globals()['Nay20{}'.format(num)] - globals()['Nay10{}'.format(num)])
                globals()['NaOffset{}'.format(num)] = HIGH_K3 - (
                            (globals()['Nay20{}'.format(num)]) * (globals()['NaRatio{}'.format(num)]))
            elif num == 1:
                globals()['NaRatio{}'.format(num)] = (HIGH_Ca2 - LOW_Ca2) / (
                            globals()['Nay20{}'.format(num)] - globals()['Nay10{}'.format(num)])
                globals()['NaOffset{}'.format(num)] = HIGH_Ca2 - (
                            (globals()['Nay20{}'.format(num)]) * (globals()['NaRatio{}'.format(num)]))    
            else:
                globals()['NaRatio{}'.format(num)] = (HIGH_Ca1 - LOW_Ca1) / (
                            globals()['Nay20{}'.format(num)] + globals()['Nay10{}'.format(num)])
                globals()['NaOffset{}'.format(num)] = HIGH_Ca1 - (
                            (globals()['Nay20{}'.format(num)]) * (globals()['NaRatio{}'.format(num)]))

            globals()['NA{}'.format(num)] = (globals()['NaRatio{}'.format(num)]) * (globals()['NaS{}'.format(num)]) + (
            globals()['NaOffset{}'.format(num)])
            #if num == 2:
            #    globals()['result{}'.format(num)] = math.pow(10, ((globals()['NA{}'.format(num)]) - 0.8406) / (
            #                -0.018 * 2.302585093))
            
            if num == 2:
                globals()['result{}'.format(num)] = math.pow(10, ((globals()['NA{}'.format(num)]) - 1.2392) / (
                            -0.02 * 2.302585093))
            elif num == 3:
                globals()['result{}'.format(num)] = math.pow(10, ((globals()['NA{}'.format(num)]) - 1.2392) / (
                            -0.02 * 2.302585093))
            elif num == 4:
                globals()['result{}'.format(num)] = math.pow(10, ((globals()['NA{}'.format(num)]) - 1.2277) / (
                            -0.02 * 2.302585093))           
            #elif num == 5:
            #    globals()['result{}'.format(num)] = math.pow(10, ((globals()['NA{}'.format(num)]) - 1.1404) / (
            #                -0.02 * 2.302585093))
            elif num == 5:
                globals()['result{}'.format(num)] = math.pow(10, ((globals()['NA{}'.format(num)]) - 0.9811) / (
                            0.015 * 2.302585093))
            elif num == 6:
                globals()['result{}'.format(num)] = math.pow(10, ((globals()['NA{}'.format(num)]) - 0.9811) / (
                            0.015 * 2.302585093))
            elif num == 7:
                globals()['result{}'.format(num)] = math.pow(10, ((globals()['NA{}'.format(num)]) - 1.0068) / (
                            0.0165 * 2.302585093))
            elif num == 1:
                globals()['result{}'.format(num)] = math.pow(10, ((globals()['NA{}'.format(num)]) - 1.6711) / (
                            -0.016 * 2.302585093))
            else:
                globals()['result{}'.format(num)] = math.pow(10, ((globals()['NA{}'.format(num)]) - 1.6711) / (
                            -0.016 * 2.302585093))

    repeat = 0
            
    
def calibration():               
###################LOW#######################
    #drain pump = 18 , low pump = 17   5.1ml/s
    #print(nowDatetime)
    #inital drain
    p.output(18, False); time.sleep(45);p.output(18, True); time.sleep(1)   #drain
    #low rinsing
    p.output(17, False); time.sleep(23.14); p.output(17, True); time.sleep(60)    #rinse
    #low drain
    p.output(18, False); time.sleep(30); p.output(18, True); time.sleep(1)  #drain
    #low pumping
    p.output(17, False); time.sleep(23.14); p.output(17, True); time.sleep(120)  #LOW measure
    for i in range(8):
        LOW(i)
    for i in range(3):
        Sodium.LOW(i)
    #print('Ca1:', round(Nay100,3), 'Ca2:', round(Nay101,3), 'NO1:', round(Nay102,3), 'NO2:', round(Nay103,3), 'NO3:', round(Nay104,3), 'K1:', round(Nay105,3), 'K2:', round(Nay106,3), 'K3:', round(Nay107,3), 'Na1:', round(Sodium.Nay100,3), 'Na2:', round(Sodium.Nay101,3), 'Na3:', round(Sodium.Nay102,3))
############################################################################
        
#######################HIGH####################################
    #drain pump = 18 , high pump = 27      4ml/s
    #low drain
    p.output(18, False); time.sleep(45); p.output(18, True); time.sleep(1)  #drain
    #high rinsing
    p.output(17, False); time.sleep(24.0); p.output(14, True); time.sleep(60)  #rinse
    #high drain
    p.output(18, False); time.sleep(30); p.output(18, True); time.sleep(1)  #drain
    #high pumping
    p.output(14, False); time.sleep(22.0); p.output(14, True); time.sleep(120) #HIGH measure
    for i in range(8):
        HIGH(i)
    for i in range(3):
        Sodium.HIGH(i)
    #print('Ca1:', round(Nay200,3), 'Ca2:', round(Nay201,3), 'NO1:', round(Nay202,3), 'NO2:', round(Nay203,3), 'NO3:', round(Nay204,3), 'K1:', round(Nay205,3), 'K2:', round(Nay206,3), 'K3:', round(Nay207,3), 'Na1:', round(Sodium.Nay200,3), 'Na2:', round(Sodium.Nay201,3), 'Na3:', round(Sodium.Nay202,3))
############################################################################
        
#############################Mixing Tank, 혼합탱크 측정 ###################################
    #drain pump = 18 , Mixing Tank sampling pump = 17       5.1ml/s
    #high drain
    p.output(18, False); time.sleep(45); p.output(18, True); time.sleep(1)   #drain
    #sample rinsing
    p.output(17, False); time.sleep(24); p.output(15, True); time.sleep(60)   #rinse
    #sample drain
    p.output(18, False); time.sleep(30); p.output(18, True); time.sleep(1)   #drain
    #sample pumping
    p.output(15, False); time.sleep(20); p.output(15, True); time.sleep(120) #Mixing Tank sample measure
    for i in range(8):
        NUTRIENT(i)
    for i in range(3):
        Sodium.NUTRIENT(i)
    #print('Ca1:', round(NaS0,3), 'Ca2:', round(NaS1,3), 'NO1:', round(NaS2,3), 'NO2:', round(NaS3,3), 'NO3:', round(NaS4,3), 'K1:', round(NaS5,3), 'K2:', round(NaS6,3), 'K3:', round(NaS7,3), 'Na1:', round(Sodium.NaS0,3), 'Na2:', round(Sodium.NaS1,3), 'Na3:', round(Sodium.NaS2,3))
############################################################################
    Sodium.result_0 = round(Sodium.result0,3); Sodium.result_1 = round(Sodium.result1,3); Sodium.result_2 = round(Sodium.result2,3)
##########Average ISE result shown here. ########### 여기는 측정한 센서의 3개 값중 어떤 값을 예측값으로 선택하는지에 관한 코드가 있는 부분
    Na_minus0 = abs(Sodium.result_0 - Sodium.result_1)
    Na_minus1 = abs(Sodium.result_1 - Sodium.result_2)
    Na_minus2 = abs(Sodium.result_0 - Sodium.result_2)
    Na_min = min(Na_minus0, Na_minus2, Na_minus1)
    Na_value_select0 = (Sodium.result_0 + Sodium.result_1)/2
    Na_value_select1 = (Sodium.result_1 + Sodium.result_2)/2
    Na_value_select2 = (Sodium.result_0 + Sodium.result_2)/2
    if Na_min == Na_minus0 :
        Na_final_value = Sodium.result_0
    elif Na_min == Na_minus1 :
        Na_final_value = Sodium.result_0
    elif Na_min == Na_minus2 :
        Na_final_value = Sodium.result_0
    result_0 = round(result0,3); result_1 = round(result1,3); result_2 = round(result2,3); result_3 = round(result3,3); result_4 = round(result4,3); result_5 = round(result5,3); result_6 = round(result6,3); result_7 = round(result7,3)
#####################
    NO3_minus0 = abs(result_2 - result_3)
    NO3_minus1 = abs(result_2 - result_4)
    NO3_minus2 = abs(result_3 - result_4)
    NO3_min = min(NO3_minus0, NO3_minus2, NO3_minus1)
    NO3_value_select0 = (result_2 + result_3)/2
    NO3_value_select1 = (result_2 + result_4)/2
    NO3_value_select2 = (result_3 + result_4)/2
    if NO3_min == NO3_minus0 :
        NO3_final_value = NO3_value_select0
    elif NO3_min == NO3_minus1 :
        NO3_final_value = NO3_value_select1
    elif NO3_min == NO3_minus2 :
        NO3_final_value = NO3_value_select2
        
    K_minus0 = abs(result_5 - result_6)
    K_minus1 = abs(result_5 - result_7)
    K_minus2 = abs(result_6 - result_7)
    K_min = min(K_minus0, K_minus2, K_minus1)
    K_value_select0 = (result_5 + result_6)/2
    K_value_select1 = (result_5 + result_7)/2
    K_value_select2 = (result_6 + result_7)/2
    if K_min == K_minus0 :
        K_final_value = K_value_select0
    elif K_min == K_minus1 :
        K_final_value = K_value_select1
    elif K_min == K_minus2 :
        K_final_value = K_value_select2

    Ca_final_value = result_1#(result_0+result_1)/2
    #Ca_final_value = result_1
    p_Na=round(Na_final_value)
    p_Ca=round(Ca_final_value)
    p_NO3=round(NO3_final_value)
    p_K=round(K_final_value)
    print(str(p_Ca).zfill(4), str(p_NO3).zfill(4), str(p_K).zfill(4), str(p_Na).zfill(4)) 
#######################Data Save###############################################
    if Ca_final_value < 500 and NO3_final_value < 1500 and K_final_value < 1000 and Na_final_value < 5000 :
        f = open('ion-monitoring.csv', 'a', newline='')
        wr = csv.writer(f)
        wr.writerow([(nowDatetime), Ca_final_value, NO3_final_value, K_final_value, Na_final_value, "good"])
        f.close()
        #g = open('monitoringdata_simplified.csv', 'a', newline='')
        #wr = csv.writer(g)
        #wr.writerow(['Date', 'MT-K', 'MT-NO3', 'MT-Ca', 'MT-Na', 'EFFLU-K', 'EFFLU-NO3', 'EFFLU-Ca', 'EFFLU-Na', 'RAIN-K', 'RAIN-NO3', 'RAIN-Ca', 'RAIN-Na', 'UNDER-K', 'UNDER-NO3', 'UNDER-Ca', 'UNDER-Na', 'Target MT', 'MTWL', 'ETWL', 'RTWL', 'UTWL','Re-K', 'Re-NO3', 'Re-Ca', 'Re-NH4', 'Re-Mg', 'Re-P' ])
        #wr.writerow([(nowDatetime), K_final_value, NO3_final_value, Ca_final_value, Na_final_value, Efflu_K_final_value, Efflu_NO3_final_value, Efflu_Ca_final_value, Efflu_Na_final_value, rain_K_final_value, rain_NO3_final_value, rain_Ca_final_value, rain_Na_final_value, under_K_final_value, under_NO3_final_value, under_Ca_final_value, under_Na_final_value, Target_Volume, WL_Mixing_Tank, WL_Effluent_Tank, WL_Rain_Tank, WL_Underground_Tank, K_Required, NO3_Required, Ca_Required, NH4_Required, Mg_Required, P_Required])
        #g.close()
        
    low_0 = round(Nay100,3); low_1 = round(Nay101,3); low_2 = round(Nay102,3); low_3 = round(Nay103,3); low_4 = round(Nay104,3); low_5 = round(Nay105,3); low_6 = round(Nay106,3); low_7 = round(Nay107,3)
    high_0 = round(Nay200,3); high_1 = round(Nay201,3); high_2 = round(Nay202,3); high_3 = round(Nay203,3); high_4 = round(Nay204,3); high_5 = round(Nay205,3); high_6 = round(Nay206,3); high_7 = round(Nay207,3)
    sample_0 = round(NaS0,3); sample_1 = round(NaS1,3); sample_2 = round(NaS2,3); sample_3 = round(NaS3,3); sample_4 = round(NaS4,3); sample_5 = round(NaS5,3); sample_6 = round(NaS6,3); sample_7 = round(NaS7,3)
    ratio_0 = round(NaRatio0,3); ratio_1 = round(NaRatio1,3); ratio_2 = round(NaRatio2,3); ratio_3 = round(NaRatio3,3); ratio_4 = round(NaRatio4,3); ratio_5 = round(NaRatio5,3); ratio_6 = round(NaRatio6,3); ratio_7 = round(NaRatio7,3)
    offset_0 = round(NaOffset0,3); offset_1 = round(NaOffset1,3); offset_2 = round(NaOffset2,3); offset_3 = round(NaOffset3,3); offset_4 = round(NaOffset4,3); offset_5 = round(NaOffset5,3); offset_6 = round(NaOffset6,3); offset_7 = round(NaOffset7,3)
    compen_0 = round(NA0,3); compen_1 = round(NA1,3); compen_2 = round(NA2,3); compen_3 = round(NA3,3); compen_4 = round(NA4,3); compen_5 = round(NA5,3); compen_6 = round(NA6,3); compen_7 = round(NA7,3)
    Sodium.low_0 = round(Sodium.Nay100,3); Sodium.low_1 = round(Sodium.Nay101,3); Sodium.low_2 = round(Sodium.Nay102,3)
    Sodium.high_0 = round(Sodium.Nay200,3); Sodium.high_1 = round(Sodium.Nay201,3); Sodium.high_2 = round(Sodium.Nay202,3)
    Sodium.sample_0 = round(Sodium.NaS0,3); Sodium.sample_1 = round(Sodium.NaS1,3); Sodium.sample_2 = round(Sodium.NaS2,3)
    Sodium.ratio_0 = round(Sodium.NaRatio0,3); Sodium.ratio_1 = round(Sodium.NaRatio1,3); Sodium.ratio_2 = round(Sodium.NaRatio2,3)
    Sodium.offset_0 = round(Sodium.NaOffset0,3); Sodium.offset_1 = round(Sodium.NaOffset1,3); Sodium.offset_2 = round(Sodium.NaOffset2,3)
    Sodium.compen_0 = round(Sodium.NA0,3); Sodium.compen_1 = round(Sodium.NA1,3); Sodium.compen_2 = round(Sodium.NA2,3)
    f = open('K3-dosing_data_specific.csv', 'a', newline='')
    wr = csv.writer(f)
    wr.writerow(['Date', 'ISE', 'Low', 'Nutrient', 'High', 'Nut PPM', 'Ratio', 'Offset', 'Nut Compen'])
    wr.writerow([(nowDatetime), 'Ca_1', low_0, sample_0, high_0, result_0, ratio_0, offset_0, compen_0])
    wr.writerow([(nowDatetime), 'Ca_2', low_1, sample_1, high_1, result_1, ratio_1, offset_1, compen_1])
    wr.writerow([(nowDatetime), 'NO3_1', low_2, sample_2, high_2, result_2, ratio_2, offset_2, compen_2])
    wr.writerow([(nowDatetime), 'NO3_2', low_3, sample_3, high_3, result_3, ratio_3, offset_3, compen_3])
    wr.writerow([(nowDatetime), 'NO3_3', low_4, sample_4, high_4, result_4, ratio_4, offset_4, compen_4])
    wr.writerow([(nowDatetime), 'K_1', low_5, sample_5, high_5, result_5, ratio_5, offset_5, compen_5])
    wr.writerow([(nowDatetime), 'K_2', low_6, sample_6, high_6, result_6, ratio_6, offset_6, compen_6])
    wr.writerow([(nowDatetime), 'K_3', low_7, sample_7, high_7, result_7, ratio_7, offset_7, compen_7])
    wr.writerow([(nowDatetime), 'Na_1', Sodium.low_0, Sodium.sample_0, Sodium.high_0, Sodium.result_0, Sodium.ratio_0, Sodium.offset_0, Sodium.compen_0])
    wr.writerow([(nowDatetime), 'Na_2', Sodium.low_1, Sodium.sample_1, Sodium.high_1, Sodium.result_1, Sodium.ratio_1, Sodium.offset_1, Sodium.compen_1])
    wr.writerow([(nowDatetime), 'Na_3', Sodium.low_2, Sodium.sample_2, Sodium.high_2, Sodium.result_2, Sodium.ratio_2, Sodium.offset_2, Sodium.compen_2])
    wr.writerow([''])
    f.close()
    '''
    Ca_r1 = abs(ratio_0)
    Ca_r2 = abs(ratio_1)
    NO_r1 = abs(ratio_2)
    NO_r2 = abs(ratio_3)
    NO_r3 = abs(ratio_4)
    K_r1 = abs(ratio_5)
    K_r2 = abs(ratio_6)
    K_r3 = abs(ratio_7)
    S_r1 = abs(Sodium.ratio_0)
    S_r2 = abs(Sodium.ratio_1)
    S_r3 = abs(Sodium.ratio_2)

    if Ca_r1 > 2 or Ca_r1 <0.5:
        print('Ca1 need change')
    if Ca_r2 > 2 or Ca_r2 <0.5:
        print('Ca2 need change')
    if NO_r1 > 2 or NO_r1 <0.5:
        print('NO3-1 need change')
    if NO_r2 > 2 or NO_r2 <0.5:
        print('NO3-2 need change')
    if NO_r3 > 2 or NO_r3 <0.5:
        print('NO3-3 need change')
    if K_r1 > 2 or K_r1 <0.5:
        print('K1 need change')
    if K_r2 > 2 or K_r2 <0.5:
        print('K2 need change')
    if K_r3 > 2 or K_r3 <0.5:
        print('K3 need change')
    if S_r1 > 2 or S_r1 <0.5:
        print('S1 need change')
    if S_r2 > 2 or S_r2 <0.5:
        print('S2 need change')
    if S_r3 > 2 or S_r3 <0.5:
        print('S3 need change')
    '''
calibration()
