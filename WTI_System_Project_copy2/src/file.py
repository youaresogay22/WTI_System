"""
title : function about the file module
author : YONG HWAN KIM (yh.kim951107@gmail.com)
date : 2020-07-14
detail : 
todo : init.. 함수에서 label 싱크로를 맞춰주어야함
"""

import os
import csv
import machine_learn
import filePath
import prePro
import pandas
import probe
import beacon
import numpy as np
"""make directory
res
    packet
        -probe
        -becon
    pcapng
    pcapng_csv
    model
    scan
        -probe
        -beacon
"""
def init_directory():
    make_Directory(filePath.res_path)      #res
    make_Directory(filePath.packet_path)   #packet
    make_Directory(filePath.probe_path)    #probe
    make_Directory(filePath.probe_test_path) #probe_test
    make_Directory(filePath.beacon_path)   #becon
    make_Directory(filePath.beacon_test_path) #becon_test
    make_Directory(filePath.pf_path)       #pcapng
    make_Directory(filePath.csv_path)      #pcapng_csv
    make_Directory(filePath.pcapng_csv_learn) #learn
    make_Directory(filePath.pcapng_csv_test) #test
    make_Directory(filePath.model_path)    #model
    make_Directory(filePath.scan_path)          #scan      
    make_Directory(filePath.scan_probe_path)    #probe
    make_Directory(filePath.scan_beacon_path)   #beacon
    make_Directory(filePath.packet_test)    #packet_test
    make_Directory(filePath.packet_test_probe_path) #probe
    make_Directory(filePath.packet_test_beacon_path) #beacon
    
 
"""make the Directory
remove the directory of path and
create the directory to path(Arg)
"""
def make_Directory(path):
    os.system("sudo rm -r "+path)

    if not os.path.exists(path):
        os.mkdir(path)
        os.system("sudo chmod 777 "
                        +path)      
        print("Directory ",path," created")
    else:
        print("Directory ",path," already exist")

"""make the Directory
create the directory for each the wlan.sa to the path(Arg)
"""
def make_macDirectory(path,mac_list):
    for mac_name in mac_list:
        os.system("sudo rm -r {}".format(path+mac_name))
        os.system("sudo mkdir {}".format(path+mac_name))

"""make feature csv file
make feature csv file about probe-request or becon-frame
"""
def make_csvFeature(path,mac,frame="seq"):
    if frame=="seq":
        mac = mac.replace(":","_")
    elif frame=="beacon":
        mac = mac.replace(":","_")

    csvFeatureFileName = path+mac+"/"+mac+"_"+"FeatureModel.csv"
    with open(csvFeatureFileName,"w") as f:
        writer = csv.writer(f)
        if frame=="seq":
            writer.writerow(["delta seq no","length","label"])
        elif frame=="beacon":
            writer.writerow(["Clock skew","RSS","Channel","duration","SSID","Mac address"])

"""add frame data
add frame data about probe-request or becon-frame to csv file
"""
def save_csvFile(path,mac_dc,interval):
    col = 1
    if interval==10:    #probe-request
        col = 1
    elif interval==3:   #becon-frame
        col = 3

    for k in mac_dc.keys():
        value = mac_dc[k]

        for i in range(len(value)): #transfer received time from time to hour, minute, second
            sec = int(float(value[i][col]))
            h, m = prePro.trans_time(sec,interval)
            csv_filename = path + k + "/" + k + "_" + str(h) + "_" + str(m) +".csv"
            
            with open(csv_filename,"a") as f: # update the csv file
                writer = csv.writer(f)
                writer.writerow(value[i])

def read_csv(csvfile):
    x_train = []
    y_train = []

    colnames = ['sa','time_relative','seq','ssid','len']
    data = pandas.read_csv(csvfile,names=colnames)
    time=data.time_relative.tolist()
    seq=data.seq.tolist()
    
    for a in time:
        x_train.append(a)
    for b in seq:
        y_train.append(b)
    return x_train, y_train

def init_seq_FeatureFile(data, mac_list, probe_path, device_dic, csvname="probe"):
    fm_name_list = []
    for mac in mac_list:
        dt, ds = probe.process_delta(mac,csvname)
        
        #probe-request 데이터가 부족하거나 없는경우
        if not dt or not ds:
            continue

        pattern = probe.linear_regression(dt,ds,mac)
 
        #FeatureModel.csv 파일 경로 설정
        dev_bssid = mac.replace(":","_")
        ospath = probe_path + dev_bssid + "/" + dev_bssid + "_FeatureModel.csv"

        fm_name_list.append(ospath)

        #시퀀스 넘버 증가율들을 리스트에 저장한다.
        delta_seq_list = []
        for item in pattern:
            delta_seq_list.append(item[0])

        #패킷 길이 저장
        temp_data = data[data["wlan.sa"]==mac]
        length = temp_data.iloc[0]["frame.len"]-len(temp_data.iloc[0]["wlan.ssid"])

        #레이블 설정
        label = 0
        for key, value in device_dic.items():
            if value==mac:
                label = key
        
        feature_line = []
        with open(ospath,"a") as f:
            for delta_seq in delta_seq_list:
                feature_line.append([delta_seq,length,label])    
            writer = csv.writer(f)
            writer.writerows(feature_line)
        
    return fm_name_list
        
    

#beacon frame value 초기화
"""write the becon-frame feature

param
bc_mac_csv_dc  : key:wlan.sa, value: csv file name list
becon_path : becon-frame directory for each mac address
return
csv_fm_list : feature csv file name list
"""
def init_beacon_FeatureFile(data,bc_mac_list,beacon_path=filePath.beacon_path):
    fm_name_list = []

    for mac in bc_mac_list:
        
        tc, to = beacon.process_clockSkew(mac,csvname="beacon")
        
        pattern = probe.linear_regression(tc,to,mac,mode="beacon")
        
        #FeatureModel.csv 파일 경로 설정
        dev_bssid = mac.replace(":","_")

        ospath = beacon_path + dev_bssid + "/" + dev_bssid + "_FeatureModel.csv"

        fm_name_list.append(ospath)

        #save the clock skew
        clock_skew = []
        for item in pattern:
            clock_skew.append(item[0])
        
        
        rss = int(data[data["wlan.sa"]==mac]["wlan_radio.signal_dbm"].mode()[0])
        
        channel = int(data[data["wlan.sa"]==mac]["wlan.ds.current_channel"].mode()[0])
        
        duration = int(data[data["wlan.sa"]==mac]["wlan_radio.duration"][0])

        ssid = str(data[data["wlan.sa"]==mac]["wlan.ssid"][0])

        mac_addr = str(data[data["wlan.sa"]==mac]["wlan.sa"][0])

        
        
        feature_line = []
        with open(ospath,"a") as f:
            for cs in clock_skew:
                feature_line.append([cs,rss,channel,duration,ssid,mac_addr])    
            writer = csv.writer(f)
            writer.writerows(feature_line)
        
    return fm_name_list

"""find the mode
count the number in  becon-frame linst
"""
def Counter(x):
    dictionary = {}
    result = 0
    for i in x:
        if dictionary.get(i) is None:
            dictionary[i] = 1
        else:
            dictionary[i] +=1

    most = max(dictionary.values())
    for key, value in dictionary.items():
        if value == most: #find the key for return the rss value
                result = key
    return result


"""make csv file for each the wlan.sa

params
path : save path
mac_list : wlan.sa list
m_interval : minute interval
end_hour : iterator end number
end_min : iterator end number
return
mac_csv_dc : key:wlan.sa, value : csv file name list
"""
def make_macCsvFile(path, mac_list, m_interval, end_hour=24, end_min = 60):
    mac_csv_dc = {}
    csv_nameList = []

    for mac_name in mac_list: #Set key: wlan.sa, value : empty list
        mac_csv_dc.update({mac_name:[]})
    
    for mac_name in mac_list:   #make csv file names
        for hour in range(0,end_hour,1):
            for minute in range(0,end_min,m_interval):
                str_hour = str(hour)
                str_minute = str(minute)
                if hour < 10:
                    str_hour = "0"+str(hour)
                if minute < 10:
                    str_minute = "0"+str(minute)
                csv_filename = path+mac_name+"/" + mac_name + "_" + str_hour + "_" + str_minute + ".csv"
                csv_nameList.append(csv_filename)

                mac_csv_dc[mac_name].append(csv_filename)   #return data

    for csvName in csv_nameList:    # create csv file
        with open(csvName,"w") as f:
            csv.writer(f)
    
    return mac_csv_dc