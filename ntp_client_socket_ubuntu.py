# client
import socket
import time 
from numpy import argmin, array, transpose
from collections import OrderedDict
import threading
import pickle
from matplotlib import pyplot as plt
import struct
from ntp_packet import Packet
import pandas as pd

logfn =""
rawStats={}
# def initialize_connection():
UDP_IP = "128.110.216.170"
UDP_PORT = 5096
client = socket.socket(socket.AF_INET, # Internet
                    socket.SOCK_DGRAM) # UDP
print("Connected to UDP target IP: %s" % UDP_IP)
print("UDP target port: %s" % UDP_PORT)
    
def createPacket():
    data = '\x1b' + 47 * '\0'; # Hex message to send to the server.
    epoch = 2208988800
    data[10]

def updateTime(offset):
    correctedTime = time.time() + offset
    clk_id = time.CLOCK_REALTIME
    time.clock_settime(clk_id, correctedTime)
    return
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

    updateTime(o)
    
    return 

def getStats(t1,t2,t3,t4):
    delay = (t4 - t1) - (t3-t2)
    offset = ((t2-t1)+(t3-t4))/2
    return offset,delay

def evaluate(running_time=600,st = 240):
    global logfn

    # initialize evaluation start time and log file, metrics
    stats = OrderedDict()
    burstID=0

    start = time.time()
    logfn = f"log_{start}.pkl"
    # run script for the intended time -defaul is 1 hour
    stats = {}
    while   (time.time()-start) <= running_time:
        print("burst# ",burstID)
        for i in range(8):
            t = time.time()
            ntp = Packet(tx_timestamp=t)
            data = ntp.marshal()
            client.sendto(data,(UDP_IP,UDP_PORT))

            data, addr = client.recvfrom(64)
            rec = time.time()
            ntp.unmarshal(data)          
            offset,delay = getStats(ntp.orig_timestamp,ntp.recv_timestamp,ntp.tx_timestamp,rec)
            rawStats[(burstID,i)]=[ntp.orig_timestamp,ntp.recv_timestamp,ntp.tx_timestamp,rec]
            stats[(burstID,i)]=[delay,offset,0,0]
            # print(f"Response:\n {str(response)}")
        thread = threading.Thread(target = process_burst, args=(stats,))
        thread.start()
        burstID+=1
        time.sleep(st)

    with open(logfn, "wb") as f:
        pickle.dump(stats,f)
    with open("rawdata", "wb") as f:
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
    
evaluate() 
plotlogs()
# x = pd.DataFrame.from_dict(rawStats)
# x = x.transpose()
# x.to_csv("raw.csv")
