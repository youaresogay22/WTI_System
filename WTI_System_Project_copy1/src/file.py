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

"""write the probe-request's feature data
write the sequnce number delta, length, label.
sequence number delta is saved to using linear_regression.
"""
def init_seq_FeatureFile(mac_csv_dc, probe_path, device_dic):
    time_list = []          #frame.time_relative
    seqNum_list = []    #sequence number delta
    csv_fm_list = []      #feature csv file names
    W = 0                     #delta
    label_val = 0

    for key,value in mac_csv_dc.items():
    
        for idx in range(len(value)):
            csvFile = value[idx]           
            x_train = machine_learn.make_timeRelative_list(csvFile)
            y_train = machine_learn.make_seqNumberList(csvFile)
            
            
            
            if len(x_train)<14:
                continue
            
            if key in device_dic.values():
                for dd_label, mac in device_dic.items():
                    if mac==key:
                        label_val = dd_label
                        break
            else:
                continue

            if not x_train or not y_train:
                continue
            else:
                W = float(machine_learn.tensor_linear_regression(x_train,y_train)) #get seqeuce number delta
                
            csv_fm = probe_path + key + "/" + key + "_FeatureModle.csv" #make feature file name
            
            if csv_fm not in csv_fm_list: #save the featuremodel.csv name
                csv_fm_list.append(csv_fm)

            
            with open(csvFile,"r") as f:    #save the length
                rdr = csv.reader(f)
                temp_rdr = rdr.__next__()
                length = temp_rdr[3]

            
            with open(csv_fm,"a") as f: #write the probe-request features
                feature_line = [W,length,label_val]
                writer = csv.writer(f)
                writer.writerow(feature_line)
            
    return csv_fm_list, device_dic

def init_seq_FeatureFile2(data, mac_list, probe_path, device_dic):
    for mac in mac_list:
        dt, ds = probe.process_delta(mac)
        pattern = probe.linear_regression(dt,ds)
        
        #FeatureModel.csv 파일 경로 설정
        dev_bssid = mac.replace(":","_")
        ospath = filePath.probe_path + dev_bssid + "/" + dev_bssid + "_FeatureModel.csv"

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
        
        with open(ospath,"a") as f:
            feature_line = [delta_seq_list]
            writer = csv.writer(f)
            writer.writerows(feature_line)
        

        
    

#beacon frame value 초기화
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
                        x_train.append([float(bc_list[idx][2])]) # i th wlan.fixed.timestamp
                        y_train.append([(float(bc_list[idx][3])  # (i th frame.time_relative - 0th frame.time_relative) - i th wlan.fixed.timestamp
                                                -float(bc_list[0][3]))
                                                -float(bc_list[idx][2])])
                        rss_list.append(int(bc_list[idx][5]))       # wlan_radio.signal_dbm

                if x_train and y_train:
                    
                    W = float(machine_learn.sklearn_linear_regression(x_train,y_train)) # clock skew
                    
                    rss_value = Counter(rss_list) # RSS

                    channel = int(bc_list[0][4]) # wlands.current_channel

                    duration = int(bc_list[0][6]) # wlan_radio.duration

                    ssid = bc_list[0][1] # wlan.ssid

                    mac_addr = bc_list[0][0] # wlan.sa
                    
                    csv_fm = becon_path + key + "/" + key + "_FeatureModle.csv"
                    
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