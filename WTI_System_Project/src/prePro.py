"""
title : preprocessor about frame
author : YONG HWAN KIM (yh.kim951107@gmail.com)
date : 2020-06-22
detail : 
todo :
"""

import csv
import copy
import filePath
import pandas as pd
import math

from pandas import DataFrame

"""preprocessor wlan.seq
convert 0~4096 to 0~infinite
"""
def preReq_Prepro():
    seq_list = []               #wlan.seq
    seq_temp_list = []    #temp wlan.seq
    length_list = []          #frame.len
    ssid_list = []              #wlan.ssid
    cycle=0                     #cycle count

    """get probe-request data
    save the data to list about wlan.seq, frame.len, wlan.ssid
    """
    csv_file = pd.read_csv(filePath.csv_probe_path)
    seq_list = list(csv_file["wlan.seq"])
    length_list = list(csv_file["frame.len"])
    ssid_list = list(csv_file["wlan.ssid"])
    seq_temp_list = copy.deepcopy(seq_list) #copy wlan.seq list
    
    for idx in range(len(seq_list)): #preprocess the wlan.seq
        if idx!=0 and int(seq_list[idx])<int(seq_list[idx-1]):
            cycle = cycle + 1
        seq_temp_list[idx] = int(seq_list[idx]) + (cycle*4096)

        if type(ssid_list[idx]) is str: # check the null ssid
            length_list[idx] = int(length_list[idx]) - len(ssid_list[idx])

    seq_list = copy.deepcopy(seq_temp_list)
    csv_file["wlan.seq"] = seq_list
    csv_file["frame.len"] = length_list
    
    data_df = DataFrame(csv_file)
    data_df.to_csv(filePath.csv_probeRe_path,sep=",",na_rep="NaN",index=False) #write csv file

"""preprocessor becon-frame data
process the wlan.fixed.timestamp data

params
bc_mac_csv_dc : key:wlan.sa value: csv file names
"""
def beacon_prepro(bc_mac_csv_dc):
    csv_list = []   #csv file names
    bc_list=[]      #becon-frame datas
    time_zero = 0   #0th wlan.fixed.timestamp

    for key in bc_mac_csv_dc.keys():        
        csv_list = copy.deepcopy(bc_mac_csv_dc[key])
        
        for csv_file in csv_list:
            
            with open(csv_file,"r") as f:
                rdr = csv.reader(f)

                #get 0th timestamp and process timestamp
                try:
                    line = next(rdr)
                    time_zero = line[2]                                                 #save timestamp
                    line[2] = (int(line[2]) - int(time_zero))/1000000   #process timestamp
                    bc_list.append(line)                                                #add the updated becon-frame
                except:
                    continue

                #process the other becon-frame timestamp 
                for line in rdr:
                    line[2] = (int(line[2]) - int(time_zero))/1000000
                    bc_list.append(line)

            with open(csv_file,"w") as f:
                writer = csv.writer(f)
                writer.writerows(bc_list) 
            bc_list = []    #초기화

"""get hour,minute
params
sec : second
interval : probe-request => 10, becon-frame => 3

return
hour, minute
"""
def trans_time(sec,interval):
    #시간, 분 계산
    s = sec

    h = int(s // 3600)
    s = int(s%3600)

    m = int(s//60)
    m = (m//interval)*interval
    
    if h<10:
        h = "0"+str(h)
    if m<10:
        m = "0"+str(m)

    return str(h), str(m)

"""extract wlan.sa

params
path : file path to extract wlan.sa
"""
def extract_macAddress(path):
    csv_file = pd.read_csv(path)
    return list(set(csv_file["wlan.sa"])) #unique and list
    
"""extract column data
extaract column data in csv file

params
rdr : readed csv file
idx : index

return
list : column datas
"""
def extract_data_index(rdr,idx):
    list = []
    for line in rdr:
        list.append(line[idx])
    return list

"""extract frame data
params
path : file path
mac_list : wlan.sa list

return
mac_dc : key:wlan.sa value: frame
"""
def extract_packetLine(path,mac_list):
    mac_dc = {}

    for mac_name in mac_list:   # dictionary initionize
        mac_dc.update({mac_name:[]})
    
    with open(path,"r") as f:
        rdr = csv.reader(f)
        packet_list=[]

        
        for line in rdr: # append from rdr to packet_list
            packet_list.append(line);

        for mac_name in mac_list: # classifiy frame data
            for line in packet_list:
                if line[0]==mac_name: #check the wlan.sa
                    mac_dc[mac_name].append(line)
    
    return mac_dc