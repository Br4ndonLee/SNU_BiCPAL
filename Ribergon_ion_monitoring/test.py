#!/usr/bin/python3

import os, sys
import time

EXPORT203="rm /home/kjh/Desktop/ise_code/low.txt"
EXPORT204="/root/ise_console_low2"

os.system(EXPORT203)

first_start = time.time()

# time.sleep(120)
for i in range(0,20):
    #start = time.time()
    os.system(EXPORT204)
    #time.sleep(0.5)
    #end = time.time()
    #print(end - start)

last_end = time.time()
print("low measurement done")
print(last_end - first_start)
