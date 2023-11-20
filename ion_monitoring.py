"""CH8.ipynb
2023.3.1
Ion Monitoring System
Dosing Algorithm - JooShin Kim, Revised by Chanmin Park
"""
import csv  #csv파일 읽기 위한 모듈
import datetime as dt   #날짜, 시간 처리하기 위한 모듈
from multiprocessing import Process    #멀티 프로세싱을 위한 모듈
import RPi.GPIO as p    #라즈베리파이 센서 제어를 위한 모듈
import time    #시간 관련 모듈
import serial   #시리얼 통신 사용을 위한 모듈
import math    #수학 함수 모듈
import sys    #프로그램에 인수를 전달하기 위한 모듈
from datetime import datetime
import spidev    #라즈베리파이 spi버스에 연결된 장치 제어 모듈


now = dt.datetime.now()    #현재 날짜 & 시각
nowDatetime = now.strftime('%Y-%m-%d %H:%M') ##:%S second can be added
spi = spidev.SpiDev()   #spi객체
spi.open(0, 0)    #spi버스의 cs 0 신호선을 사용할 장치의 cs와 연결
spi.max_speed_hz = 1000000    #spi 동작속도


##################### GLOBAL ###############################
repeat = 0
sample = []    # for NUTRIENT
low_solution = []    # for LOW
high_solution = []    # for HIGH
# under_water = []
# effluent = []
# rainy = []


##############################################################<------------------
LOW_Ca1 = 0.0070211 * math.log10(24.96) * 2.302585093 + 0.85959
HIGH_Ca1 = 0.0070211 * math.log10(243.00) * 2.302585093 + 0.85959
LOW_Ca2 = 0.0070211 * math.log10(24.96) * 2.302585093 + 0.85959
HIGH_Ca2 = 0.0070211 * math.log10(243.00) * 2.302585093 + 0.85959
LOW_Ca3 = 0.0070211 * math.log10(24.96) * 2.302585093 + 0.85959
HIGH_Ca3 = 0.0070211 * math.log10(243.00) * 2.302585093 + 0.85959

LOW_NO1 = -0.02394 * math.log10(21.8) * 2.302585093 + 1.2482    #-0.02394*ln(21.8)+1.2482
HIGH_NO1 = -0.02394 * math.log10(712.0) * 2.302585093 + 1.2482
LOW_NO2 = -0.02394 * math.log10(21.8) * 2.302585093 + 1.2482
HIGH_NO2 = -0.02394 * math.log10(712.0) * 2.302585093 + 1.2482
LOW_NO3 = -0.02394 * math.log10(21.8) * 2.302585093 + 1.2482
HIGH_NO3 = -0.02394 * math.log10(712.0) * 2.302585093 + 1.2482

LOW_K1 = 0.023988 * math.log10(6.07) * 2.302585093 + 0.96136    # LOW와 HIGH 값은 V 단위로 구해짐.
HIGH_K1 = 0.023988 * math.log10(220.03) * 2.302585093 + 0.96136
LOW_K2 = 0.023988 * math.log10(6.07) * 2.302585093 + 0.96136
HIGH_K2 = 0.023988 * math.log10(220.03) * 2.302585093 + 0.96136
#######################GPIO_Setting############################
p.setmode(p.BCM)    #SOC 칩에서 사용하는 핀 이름 사용(GPIO##)
p.setup([18, 17, 14, 15], p.OUT, initial=p.HIGH) #Dosing Unit
              #Chamber Unit-PinNo 12, 11, 08, 10

def ReadChannel3208(channel): #MCP3208 ADC converter와 통신하기 위한 코드
    r = spi.xfer2([6 | (channel >> 2), channel << 6, 0])
    adc_out = ((r[1] & 15) << 8) + r[2]
    return adc_out


def LOW(num):               ### LOW 용액 전압 측정 코드
    global repeat
    global low_solution
    low_solution = []
    while repeat < 10000:
        repeat = repeat + 1
        input_low = ReadChannel3208(num)
        low_solution.append(input_low)
        if repeat == 10000:
            low_now = sum(low_solution, 0.0) / len(low_solution)
            globals()['Nay10{}'.format(num)] = low_now * 3.3 / 4095    # EMF는 V 단위
            #print('LOW{}: {}'.format(num, round(globals()['Nay10{}'.format(num)], 3)))
    repeat = 0


def HIGH(num):           ### HIGH 용액 전압 측정 코드
    global repeat
    global high_solution
    high_solution = []
    while repeat < 10000:
        repeat = repeat + 1
        input_high = ReadChannel3208(num)
        high_solution.append(input_high)
        if repeat == 10000:
            high_now = sum(high_solution, 0.0) / len(high_solution)
            globals()['Nay20{}'.format(num)] = high_now * 3.3 / 4095
            #print('HIGH{}: {}'.format(num, round(globals()['Nay20{}'.format(num)], 3)))
    repeat = 0


def NUTRIENT(num):    # 양액 혼합 탱크 전압 측정 및 보상 코드 
    global repeat
    global sample
    sample = []
    # sample measuring
    while repeat < 10000:
        repeat = repeat + 1
        input_sample = ReadChannel3208(num)
        sample.append(input_sample)
        if repeat == 10000:
            no12_now = sum(sample, 0.0) / len(sample)
            globals()['NaS{}'.format(num)] = no12_now * 3.3 / 4095
            #print('Nutrient{}: {}'.format(num, round(globals()['NaS{}'.format(num)], 3)))

            #################ADC의 CH0부터 CH7까지 순서대로 Ca 3개, NO3 3개, K 2개 배치######
            if num == 0:  # Ca_1
                globals()['NaRatio{}'.format(num)] = (HIGH_Ca1 - LOW_Ca1) / (
                            globals()['Nay20{}'.format(num)] + globals()['Nay10{}'.format(num)])
                globals()['NaOffset{}'.format(num)] = HIGH_Ca1 - (
                            (globals()['Nay20{}'.format(num)]) * (globals()['NaRatio{}'.format(num)]))
            elif num == 1:  # Ca_2
                globals()['NaRatio{}'.format(num)] = (HIGH_Ca2 - LOW_Ca2) / (
                            globals()['Nay20{}'.format(num)] - globals()['Nay10{}'.format(num)])
                globals()['NaOffset{}'.format(num)] = HIGH_Ca2 - (
                            (globals()['Nay20{}'.format(num)]) * (globals()['NaRatio{}'.format(num)]))    
            elif num == 2:  # Ca_3
                globals()['NaRatio{}'.format(num)] = (HIGH_Ca3 - LOW_Ca3) / (
                            globals()['Nay20{}'.format(num)] - globals()['Nay10{}'.format(num)])
                globals()['NaOffset{}'.format(num)] = HIGH_Ca3 - (
                            (globals()['Nay20{}'.format(num)]) * (globals()['NaRatio{}'.format(num)]))
            elif num == 3:  # NO3_1
                globals()['NaRatio{}'.format(num)] = (HIGH_NO1 - LOW_NO1) / (
                            globals()['Nay20{}'.format(num)] - globals()['Nay10{}'.format(num)])
                globals()['NaOffset{}'.format(num)] = HIGH_NO1 - (
                            (globals()['Nay20{}'.format(num)]) * (globals()['NaRatio{}'.format(num)]))
            elif num == 4:  # NO3_2
                globals()['NaRatio{}'.format(num)] = (HIGH_NO2 - LOW_NO2) / (
                            globals()['Nay20{}'.format(num)] - globals()['Nay10{}'.format(num)])
                globals()['NaOffset{}'.format(num)] = HIGH_NO2 - (
                            (globals()['Nay20{}'.format(num)]) * (globals()['NaRatio{}'.format(num)]))
            elif num == 5:  # NO3_3
                globals()['NaRatio{}'.format(num)] = (HIGH_NO3 - LOW_NO3) / (
                            globals()['Nay20{}'.format(num)] - globals()['Nay10{}'.format(num)])
                globals()['NaOffset{}'.format(num)] = HIGH_NO3 - (
                            (globals()['Nay20{}'.format(num)]) * (globals()['NaRatio{}'.format(num)]))    
            elif num == 6:  # K_1
                globals()['NaRatio{}'.format(num)] = (HIGH_K1 - LOW_K1) / (
                            globals()['Nay20{}'.format(num)] - globals()['Nay10{}'.format(num)])
                globals()['NaOffset{}'.format(num)] = HIGH_K1 - (
                            (globals()['Nay20{}'.format(num)]) * (globals()['NaRatio{}'.format(num)]))
            elif num == 7:  # K_2
                globals()['NaRatio{}'.format(num)] = (HIGH_K2 - LOW_K2) / (
                            globals()['Nay20{}'.format(num)] - globals()['Nay10{}'.format(num)])
                globals()['NaOffset{}'.format(num)] = HIGH_K2 - (
                            (globals()['Nay20{}'.format(num)]) * (globals()['NaRatio{}'.format(num)]))


            globals()['NA{}'.format(num)] = (globals()['NaRatio{}'.format(num)]) * (globals()['NaS{}'.format(num)]) + (
            globals()['NaOffset{}'.format(num)])
            
            # Retracking the concentration of sample
            if num == 0:  # Ca_1
                globals()['result{}'.format(num)] = math.pow(10, ((globals()['NA{}'.format(num)]) - 0.85959) / (
                            0.0070211 * 2.302585093))
            elif num == 1:  # Ca_2
                globals()['result{}'.format(num)] = math.pow(10, ((globals()['NA{}'.format(num)]) - 0.85959) / (
                            0.0070211 * 2.302585093))
            elif num == 2:  # Ca_3
                globals()['result{}'.format(num)] = math.pow(10, ((globals()['NA{}'.format(num)]) - 0.85959) / (
                            0.0070211 * 2.302585093))                                
            elif num == 3:  # NO3_1
                globals()['result{}'.format(num)] = math.pow(10, ((globals()['NA{}'.format(num)]) - 1.2482) / (
                            -0.02394 * 2.302585093))
            elif num == 4:  # NO3_2
                globals()['result{}'.format(num)] = math.pow(10, ((globals()['NA{}'.format(num)]) - 1.2482) / (
                            -0.02394 * 2.302585093))      
            elif num == 5:  # NO3_3
                globals()['result{}'.format(num)] = math.pow(10, ((globals()['NA{}'.format(num)]) - 1.2482) / (
                            -0.02394 * 2.302585093))
            elif num == 6:  #K_1
                globals()['result{}'.format(num)] = math.pow(10, ((globals()['NA{}'.format(num)]) - 0.96136) / (
                            0.023988 * 2.302585093))
            elif num == 7:  #K_2
                globals()['result{}'.format(num)] = math.pow(10, ((globals()['NA{}'.format(num)]) - 0.96136) / (
                            0.023988 * 2.302585093))
    repeat = 0
            
    
def calibration():               
###################LOW#######################
    #drain pump = 18 , low pump = 17   5.1ml/s
    #print(nowDatetime)
    #inital drain
    p.output(18, False); time.sleep(20);p.output(18, True); time.sleep(1)   #drain
    #low rinsing
    p.output(17, False); time.sleep(14.14); p.output(17, True); time.sleep(1)    #rinse
    #low drain
    p.output(18, False); time.sleep(20); p.output(18, True); time.sleep(1)  #drain
    #low pumping
    p.output(17, False); time.sleep(14.14); p.output(17, True); time.sleep(120)  #LOW measure
    for i in range(8):
        LOW(i)
    #print('Ca1:', round(Nay100,3), 'Ca2:', round(Nay101,3), 'NO1:', round(Nay102,3), 'NO2:', round(Nay103,3), 'NO3:', round(Nay104,3), 'K1:', round(Nay105,3), 'K2:', round(Nay106,3), 'K3:', round(Nay107,3), 'Na1:', round(Sodium.Nay100,3), 'Na2:', round(Sodium.Nay101,3), 'Na3:', round(Sodium.Nay102,3))
############################################################################
        
#######################HIGH####################################
    #drain pump = 18 , high pump = 27      4ml/s
    #low drain
    p.output(18, False); time.sleep(20); p.output(18, True); time.sleep(1)  #drain
    #high rinsing
    p.output(14, False); time.sleep(13.0); p.output(14, True); time.sleep(1)  #rinse
    #high drain
    p.output(18, False); time.sleep(20); p.output(18, True); time.sleep(1)  #drain
    #high pumping
    p.output(14, False); time.sleep(13.0); p.output(14, True); time.sleep(120) #HIGH measure
    for i in range(8):
        HIGH(i)
    #print('Ca1:', round(Nay200,3), 'Ca2:', round(Nay201,3), 'NO1:', round(Nay202,3), 'NO2:', round(Nay203,3), 'NO3:', round(Nay204,3), 'K1:', round(Nay205,3), 'K2:', round(Nay206,3), 'K3:', round(Nay207,3), 'Na1:', round(Sodium.Nay200,3), 'Na2:', round(Sodium.Nay201,3), 'Na3:', round(Sodium.Nay202,3))
############################################################################
        
#############################Mixing Tank, 혼합탱크 측정 ###################################
    #drain pump = 18 , Mixing Tank sampling pump = 17       5.1ml/s
    #high drain
    p.output(18, False); time.sleep(22); p.output(18, True); time.sleep(1)   #drain
    #sample rinsing
    p.output(15, False); time.sleep(26); p.output(15, True); time.sleep(1)   #rinse
    #sample drain
    p.output(18, False); time.sleep(22); p.output(18, True); time.sleep(1)   #drain
    #sample pumping
    p.output(15, False); time.sleep(26); p.output(15, True); time.sleep(120) #Mixing Tank sample measure
    for i in range(8):
        NUTRIENT(i)
    #print('Ca1:', round(NaS0,3), 'Ca2:', round(NaS1,3), 'NO1:', round(NaS2,3), 'NO2:', round(NaS3,3), 'NO3:', round(NaS4,3), 'K1:', round(NaS5,3), 'K2:', round(NaS6,3), 'K3:', round(NaS7,3), 'Na1:', round(Sodium.NaS0,3), 'Na2:', round(Sodium.NaS1,3), 'Na3:', round(Sodium.NaS2,3))
##########Average ISE result shown here. ########### 여기는 측정한 센서의 3개 값중 어떤 값을 예측값으로 선택하는지에 관한 코드가 있는 부분
    result_0 = round(result0,3)
    result_1 = round(result1,3)
    result_2 = round(result2,3)
    result_3 = round(result3,3)
    result_4 = round(result4,3)
    result_5 = round(result5,3)
    result_6 = round(result6,3)
    result_7 = round(result7,3)

    Ca_minus0 = abs(result_0 - result_1)
    Ca_minus1 = abs(result_1 - result_2)
    Ca_minus2 = abs(result_2 - result_0)
    Ca_min = min(Ca_minus0, Ca_minus1, Ca_minus2)
    Ca_value_select0 = (result_0 + result_1)/2
    Ca_value_select1 = (result_1 + result_2)/2
    Ca_value_select2 = (result_2 + result_0)/2
    if Ca_min == Ca_minus0 :
        Ca_final_value = Ca_value_select0
    elif Ca_min == Ca_minus1 :
        Ca_final_value = Ca_value_select1
    elif Ca_min == Ca_minus2 :
        Ca_final_value = Ca_value_select2
        
    NO3_minus0 = abs(result_3 - result_4)
    NO3_minus1 = abs(result_4 - result_5)
    NO3_minus2 = abs(result_5 - result_3)
    NO3_min = min(NO3_minus0, NO3_minus2, NO3_minus1)
    NO3_value_select0 = (result_3 + result_4)/2
    NO3_value_select1 = (result_4 + result_5)/2
    NO3_value_select2 = (result_5 + result_3)/2
    if NO3_min == NO3_minus0 :
        NO3_final_value = NO3_value_select0
    elif NO3_min == NO3_minus1 :
        NO3_final_value = NO3_value_select1
    elif NO3_min == NO3_minus2 :
        NO3_final_value = NO3_value_select2
        
    K_final_value = (result_6 + result_7)/2

    p_Ca=round(Ca_final_value)
    p_NO3=round(NO3_final_value)
    p_K=round(K_final_value)
    print(str(p_Ca).zfill(4), str(p_NO3).zfill(4), str(p_K).zfill(4)) 

#######################Data Save###############################################
    if Ca_final_value < 500 and NO3_final_value < 1500 and K_final_value < 1000 : # 각각 HIGH는 243, 712, 220
        f = open('ion-monitoring.csv', 'a', newline='')
        wr = csv.writer(f)
        wr.writerow([(nowDatetime), Ca_final_value, NO3_final_value, K_final_value, "good"])
        f.close()
        
    low_0 = round(Nay100,3); low_1 = round(Nay101,3); low_2 = round(Nay102,3); low_3 = round(Nay103,3); low_4 = round(Nay104,3); low_5 = round(Nay105,3); low_6 = round(Nay106,3); low_7 = round(Nay107,3)
    high_0 = round(Nay200,3); high_1 = round(Nay201,3); high_2 = round(Nay202,3); high_3 = round(Nay203,3); high_4 = round(Nay204,3); high_5 = round(Nay205,3); high_6 = round(Nay206,3); high_7 = round(Nay207,3)
    sample_0 = round(NaS0,3); sample_1 = round(NaS1,3); sample_2 = round(NaS2,3); sample_3 = round(NaS3,3); sample_4 = round(NaS4,3); sample_5 = round(NaS5,3); sample_6 = round(NaS6,3); sample_7 = round(NaS7,3)
    ratio_0 = round(NaRatio0,3); ratio_1 = round(NaRatio1,3); ratio_2 = round(NaRatio2,3); ratio_3 = round(NaRatio3,3); ratio_4 = round(NaRatio4,3); ratio_5 = round(NaRatio5,3); ratio_6 = round(NaRatio6,3); ratio_7 = round(NaRatio7,3)
    offset_0 = round(NaOffset0,3); offset_1 = round(NaOffset1,3); offset_2 = round(NaOffset2,3); offset_3 = round(NaOffset3,3); offset_4 = round(NaOffset4,3); offset_5 = round(NaOffset5,3); offset_6 = round(NaOffset6,3); offset_7 = round(NaOffset7,3)
    compen_0 = round(NA0,3); compen_1 = round(NA1,3); compen_2 = round(NA2,3); compen_3 = round(NA3,3); compen_4 = round(NA4,3); compen_5 = round(NA5,3); compen_6 = round(NA6,3); compen_7 = round(NA7,3)
    
    f = open('dosing_data_specific.csv', 'a', newline='')
    wr = csv.writer(f)
    wr.writerow(['Date', 'ISE', 'Low', 'Nutrient', 'High', 'Nut PPM', 'Ratio', 'Offset', 'Nut Compen'])
    wr.writerow([(nowDatetime), 'Ca_1', low_0, sample_0, high_0, result_0, ratio_0, offset_0, compen_0])
    wr.writerow([(nowDatetime), 'Ca_2', low_1, sample_1, high_1, result_1, ratio_1, offset_1, compen_1])
    wr.writerow([(nowDatetime), 'Ca_3', low_2, sample_2, high_2, result_2, ratio_2, offset_2, compen_2])
    wr.writerow([(nowDatetime), 'NO3_1', low_3, sample_3, high_3, result_3, ratio_3, offset_3, compen_3])
    wr.writerow([(nowDatetime), 'NO3_2', low_4, sample_4, high_4, result_4, ratio_4, offset_4, compen_4])
    wr.writerow([(nowDatetime), 'NO3_3', low_5, sample_5, high_5, result_5, ratio_5, offset_5, compen_5])
    wr.writerow([(nowDatetime), 'K_1', low_6, sample_6, high_6, result_6, ratio_6, offset_6, compen_6])
    wr.writerow([(nowDatetime), 'K_2', low_7, sample_7, high_7, result_7, ratio_7, offset_7, compen_7])
    wr.writerow([''])
    f.close()

calibration()
