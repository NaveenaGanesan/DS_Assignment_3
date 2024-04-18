# # client
import socket
import time 
from numpy import argmin, array, transpose
from collections import OrderedDict
import threading
import pickle
from matplotlib import pyplot as plt
from ntp_packet import Packet
import pandas as pd
import datetime
import os


logfn =""
rawStats={}

# def initialize_connection():
# UDP_IP = "128.110.218.145"
UDP_IP = "127.0.0.1"
UDP_PORT = 5096
client = socket.socket(socket.AF_INET, # Internet
                    socket.SOCK_DGRAM) # UDP

client.settimeout(5)
print("Connected to UDP target IP: %s" % UDP_IP)
print("UDP target port: %s" % UDP_PORT)
    

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

    # updateTime(o)
    
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
    logfn = f"log_{start}"
    stats = {}

    # run script for the intended time -default is 1 hour
    while   (time.time()-start) <= running_time:
        print("burst# ",burstID)
        for i in range(8):

            # prepare packet with current timestamp of client
            t = time.time()
            ntp = Packet(tx_timestamp=t)
            data = ntp.marshal()
            
            # send packet + positive ack
            client.sendto(data,(UDP_IP,UDP_PORT))
            while True:
                try:
                    data, addr = client.recvfrom(64)
                    break
                except socket.timeout:
                    print("Experienced timeout. Retrying")
                    client.sendto(data,(UDP_IP,UDP_PORT))
                    
            # after receiving correct time from server,
            # get values from serialized data
            rec = time.time()
            ntp.unmarshal(data)

            # calculate stats           
            offset,delay = getStats(ntp.orig_timestamp,ntp.recv_timestamp,ntp.tx_timestamp,rec)
            
            # log stats for graphs and excel
            rawStats[(burstID,i)]=[ntp.orig_timestamp,ntp.recv_timestamp,ntp.tx_timestamp,rec]
            stats[(burstID,i)]=[delay,offset,0,0]

        # process the offset and delay separately
        thread = threading.Thread(target = process_burst, args=(stats,))
        thread.start()
        burstID+=1
        time.sleep(st)

    filename = logfn+"/log.pkl"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "wb") as f:
        pickle.dump(stats,f)
    
    filename = logfn+"/rawdata.xlsx"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    # with open(filename, "w") as f:
    x = pd.DataFrame.from_dict(rawStats)
    x = x.transpose()
    x.to_excel(filename)
       
def plotlogs():
    global logfn    
    with open(logfn+"/log.pkl",'rb') as f:
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
    plt.savefig(logfn+"/graph.png")
    plt.show()
    
evaluate(240,60) 
plotlogs()

x = pd.DataFrame.from_dict(rawStats)
x = x.transpose()
x.to_excel("public_raw.xlsx")

# with open("rawdata.pkl","rb") as f:
#     x = pickle.load(f)
#     x = pd.DataFrame.from_dict(x)
#     x = x.transpose()
#     x.to_csv("public_raw.csv")