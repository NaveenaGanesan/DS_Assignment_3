# client
import socket
import ntplib
# from time import ctime, sleep,time
import time
from numpy import argmin, array, transpose
from collections import OrderedDict
import threading
import pickle
from matplotlib import pyplot as plt
# import win32api
import datetime
from ntp_packet import Packet
import pandas as pd

logfn =""
rawStats={}
def process_burst(responses):
    d,o=0,0
    for i in range(7,-1,-1):
        window = list(responses.values())[-i-8:-i]
        if i==0:
            window = list(responses.values())[-i-8:]
        minpair = argmin(array(window)[:,0])
        key = list(responses.keys())[-i-1]
        # print(window,minpair,key,sep="\n")
        d = window[minpair][0]
        o = window[minpair][1]
        responses[key][2] = d
        responses[key][3] = o

    correctedTime = time.time() + o
    # utc = datetime.datetime.utcfromtimestamp(correctedTime)
    # print(utc)
    # win32api.SetSystemTime(utc.year,utc.month,utc.weekday(),utc.day,utc.hour,utc.minute,utc.second,0)

    clk_id = time.CLOCK_REALTIME
    time.clock_settime(clk_id, correctedTime)
    return

def evaluate_ntp_public(running_time = 3600,sleeptime=60):
    global logfn
    # initialize ntp client
    c = ntplib.NTPClient()

    # initialize evaluation start time and log file, metrics
    stats = OrderedDict()
    burstID=0

    start = time.time()
    logfn = f"log_public_{start}.pkl"
    # run script for the intended time -defaul is 1 hour
    stats = {}
    while   (time.time()-start) <= running_time:
        print("burst# ",burstID)
        for i in range(8):
            t = time.time()
            response = c.request('time.nist.gov')
            rawStats[(burstID,i)]=[response.orig_timestamp,response.recv_time,response.tx_timestamp,time.time()]
            stats[(burstID,i)]=[response.delay,response.offset,0,0]
            
            # print(f"Response:\n {str(response)}")
        thread = threading.Thread(target = process_burst, args=(stats,))
        thread.start()
        burstID+=1
        time.sleep(sleeptime)

    # for i in stats:
    #     with ("debug.txt",'a') as f:
    #         f.write(f"{str(i)} : {str(stats[i])}")

    with open(logfn, "wb") as f:
        pickle.dump(stats,f)
    with open("rawdata.pkl", "wb") as f:
        pickle.dump(rawStats,f)
        
def plotlogs():
    global logfn    
    with open(logfn,'rb') as f:
        data = pickle.load(f)

    # print(data)
    keys = list(data.keys())
    x = [str(k) for k in keys]
    y = transpose(array(list(data.values())))
    plt.plot(x, y[0], label="di")
    plt.plot(x, y[1], label="oi")
    plt.plot(x, y[2], label="best delay")
    plt.plot(x, y[3], label="best offset")
    leg = plt.legend(loc='upper right')
    plt.xticks(rotation=60)
    plt.show()
    
# public NTP server
evaluate_ntp_public()

# evaluate()
plotlogs()
x = pd.DataFrame.from_dict(rawStats)
x = x.transpose()
x.to_excel("public_raw.xlsx")