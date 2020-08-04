"""
title : 파일 작성 및 참조 관련 모듈
author : 김용환 (dragonbead95@naver.com)
date : 2020-08-03
detail : 
todo :
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
from scipy import stats

"""make directory
res
    model
    packet
        -beacon
        -beacon_test
        -probe
        -probe_test
    pcapng
    pcapng_csv
        -learn
        -test
    scan
        -beacon
        -probe
"""
def init_directory():
    make_Directory(filePath.res_path)               #res
    make_Directory(filePath.packet_path)            #packet
    make_Directory(filePath.probe_path)             #probe
    make_Directory(filePath.probe_test_path)        #probe_test
    make_Directory(filePath.beacon_path)            #becon
    make_Directory(filePath.beacon_test_path)       #becon_test
    make_Directory(filePath.pf_path)                #pcapng
    make_Directory(filePath.csv_path)               #pcapng_csv
    make_Directory(filePath.pcapng_csv_learn)       #learn
    make_Directory(filePath.pcapng_csv_test)        #test
    make_Directory(filePath.model_path)             #model
    make_Directory(filePath.scan_path)              #scan      
    make_Directory(filePath.scan_probe_path)        #probe
    make_Directory(filePath.scan_beacon_path)       #beacon
    make_Directory(filePath.packet_test)            #packet_test
    make_Directory(filePath.packet_test_probe_path) #probe
    make_Directory(filePath.packet_test_beacon_path)#beacon
    
 
"""make the Directory
경로상의 디렉토리를 삭제하고 다시 경로상의 디렉토리를 생성한다.
찌꺼기 데이터가 남아있는것을 방지하기 위해서 한번 삭제한다.

params
path : 디렉터리를 생성할 경로
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

"""mac주소 디렉터리 생성
mac_list에 있는 맥주소 이름의 디렉터리 생성

params
path : 맥주소 디렉터리가 저장되는 경로 중 일부
mac_list : 기기의 맥주소가 담격있는 맥주소 리스트
"""
def make_macDirectory(path,mac_list):
    for mac_name in mac_list:
        os.system("sudo rm -rf {}".format(path+mac_name))
        os.system("sudo mkdir {}".format(path+mac_name))

"""FeatureModel.csv 파일 생성
params
path : FeatureMOdel.csv 파일을 생성할 경로 중 일부
mac : 저장 파일 경로에 사용되는 맥주소
frame : seq -> probe-request의 경우 맥주소간의 콜론을 언더바(_)로 변경한다.
"""
def make_csvFeature(path,mac,frame="seq"):
    if frame=="seq":
        mac = mac.replace(":","_")

    csvFeatureFileName = path+mac+"/"+mac+"_"+"FeatureModel.csv"
    with open(csvFeatureFileName,"w") as f:
        writer = csv.writer(f)
        if frame=="seq":
            writer.writerow(["delta seq no","length","label"])
        elif frame=="beacon":
            writer.writerow(["Clock skew","RSS","Channel","duration","SSID","Mac address"])

"""probe-request 특징 데이터를 저장한다.
params
data : 무선단말기기 정보들
mac_list : 무선단말기기 맥주소 리스트
probe_path : 저장하기 위해서 사용되는 probe-request 경로 주소 문자열
device_dic : 무선 단말 레이블 딕셔너리, 레이블을 저장하기 위해 사용된다.
csvname : 저장된 경로를 호출하기 위해 사용되는 경로 문자열이다.

return
fm_name_list : featuremodel.csv 파일 경로들이 들어있는 리스트 
"""
def init_seq_FeatureFile(data, mac_list, probe_path, device_dic, csvname="probe"):
    fm_name_list = []
    for mac in mac_list:
        #delta seq no를 구하기 위한 x_train, y_train이다.
        dt, ds = probe.process_delta(mac,csvname)
        

        #probe-request 데이터가 부족하거나 없는경우
        if not dt or not ds:
            continue

        #delta seq no를 구한다.
        pattern = probe.linear_regression(dt,ds,mac)
 
        #FeatureModel.csv 파일 경로 설정
        dev_bssid = mac.replace(":","_")
        ospath = probe_path + dev_bssid + "/" + dev_bssid + "_FeatureModel.csv"

        #리스트에 FeatureModel.csv 파일 이름 경로 추가
        fm_name_list.append(ospath)

        #시퀀스 넘버 증가율(delta seq no)들을 리스트에 저장한다.
        delta_seq_list = []
        for item in pattern:
            delta_seq_list.append(item[0])

        #패킷 길이 저장
        temp_data = data[data["wlan.sa"]==mac]
        length_list = []
        for i in range(len(temp_data)):
            length_list.append(temp_data.iloc[i]["frame.len"]-len(temp_data.iloc[i]["wlan.ssid"]))
        length = stats.mode(length_list)[0][0] #length의 최빈 value을 구하여 저장한다.
        
        #레이블 설정
        label = "-1"    #device_dic 딕셔너리에 들어있지 않은 맥주소일시 label은 -1이 된다.
        for key, value in device_dic.items():
            if value==mac:
                label = key
        
        #featuremodel.csv 파일에 데이터를 저장한다.
        feature_line = []
        with open(ospath,"a") as f:
            for delta_seq in delta_seq_list:
                feature_line.append([delta_seq,length,label])    
            writer = csv.writer(f)
            writer.writerows(feature_line)
        
    return fm_name_list
        
    
"""write the becon-frame feature

param
bc_mac_csv_dc  : key:wlan.sa, value: csv file name list
becon_path : becon-frame directory for each mac address
return
csv_fm_list : feature csv file name list
"""
def init_beacon_FeatureFile(bc_mac_csv_dc,becon_path=filePath.beacon_path):
    csv_fm_list = []    #csv feature csv file names
    bc_list = []
    x_train = []
    y_train = []
    rss_list = []
    rss_value=0
    channel = 0
    duration = 0
    ssid = ""
    mac_addr = ""

    for key, value in bc_mac_csv_dc.items():
        for idx in range(len(value)):
                csvFile = value[idx]

                with open(csvFile,"r") as f: #copy the becon-frame to the bc_list
                    rdr = csv.reader(f)
                    for line in rdr:
                        bc_list.append(line)
                
                if not bc_list:
                    continue
                else:
                    
                    for idx in range(len(bc_list)):
                        time_clock_val = float(bc_list[idx][3]) - float(bc_list[0][3]) 
                        time_offset_Val = float(bc_list[idx][2]) - float(bc_list[0][2]) - time_clock_val
                        x_train.append([time_clock_val])
                        y_train.append([time_offset_Val])
                        rss_list.append(int(bc_list[idx][5]))       # wlan_radio.signal_dbm
                if x_train and y_train:
                    
                    W = float(machine_learn.sklearn_linear_regression(x_train,y_train)) # clock skew
                    
                    print("{}".format(key) + " {}".format(W))

                    rss_value = Counter(rss_list) # RSS

                    channel = int(bc_list[0][4]) # wlands.current_channel

                    duration = int(bc_list[0][6]) # wlan_radio.duration

                    ssid = bc_list[0][1] # wlan.ssid

                    mac_addr = bc_list[0][0] # wlan.sa
                    
                    csv_fm = becon_path + key + "/" + key + "_FeatureModel.csv"
                    
                    if csv_fm not in csv_fm_list:
                        csv_fm_list.append(csv_fm)

                    with open(csv_fm,"a") as f: #write the becon-frame feature
                        feature_lline = [W,rss_value,channel,duration,ssid,mac_addr]
                        writer = csv.writer(f)
                        writer.writerow(feature_lline)
                    
                x_train = []
                y_train = []
                bc_list = []
                rss_list = []

    return csv_fm_list


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
