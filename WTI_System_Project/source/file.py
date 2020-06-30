"""
title : function about the file module
author : YONG HWAN KIM (yh.kim951107@gmail.com)
date : 2020-06-22
detail : 
todo :
"""

import os
import csv
import machine_learn
import filePath
import prePro
import pandas
"""make the Directory
remove the directory of path and
create the directory to path(Arg)
"""
def make_Directory(path):
    os.system("sudo rm -r "+path)

    if not os.path.exists(path):
        os.mkdir(path)
        print("Directory ",path," created")
    else:
        print("Directory ",path," already exist")

"""make the Directory
create the directory for each the wlan.sa to the path(Arg)
"""
def make_macDirectory(path,mac_list):
    for mac_name in mac_list:
        if not os.path.exists(path+mac_name):
            os.mkdir(path+mac_name)
            print("Directory ",path,mac_name, " created")
        else:
            print("Directory ",path,mac_name, " already exist")

"""make feature csv file
make feature csv file about probe-request or becon-frame
"""
def make_csvFeature(path,mac,frame="seq"):
    csvFeatureFileName = path+mac+"/"+mac+"_"+"FeatureModle.csv"
    with open(csvFeatureFileName,"w") as f:
        writer = csv.writer(f)
        if frame=="seq":
            writer.writerow(["delta seq no","length","label"])
        elif frame=="beacon":
            writer.writerow(["Clock skew","RSS","Channel","duration","SSID","MAC Address"])

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
def init_seq_FeatureFile(mac_csv_dc):
    time_list = []          #frame.time_relative
    seqNum_list = []    #sequence number delta
    csv_fm_list = []      #feature csv file names
    W = 0                     #delta
    label = 0                 #label

    for key,value in mac_csv_dc.items():
    
        for idx in range(len(value)):
            csvFile = value[idx]           
            x_train, y_train = read_csv(csvFile)
            
            if len(x_train)<15:
                continue

            if not x_train or not y_train:
                continue
            else:
                W = float(machine_learn.linear_regression2(x_train,y_train)) #get seqeuce number delta
            
            csv_fm = filePath.probe_path + key + "/" + key + "_FeatureModle.csv" #make feature file name

            if csv_fm not in csv_fm_list: #save the featuremodel.csv name
                csv_fm_list.append(csv_fm)

            
            with open(csvFile,"r") as f:    #save the length
                rdr = csv.reader(f)
                length = rdr.__next__()[4]
            
            with open(csv_fm,"a") as f: #write the probe-request features
                feature_lline = [W,length,label]
                writer = csv.writer(f)
                writer.writerow(feature_lline)
                   
        label += 1
    return csv_fm_list

#beacon frame value 초기화
"""write the becon-frame feature

param
bc_mac_csv_dc  : key:wlan.sa, value: csv file name list

return
csv_fm_list : feature csv file name list
"""
def init_beacon_FeatureFile(bc_mac_csv_dc):
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
                    
                    W = float(machine_learn.linear_regression(x_train,y_train)) # clock skew
                    
                    rss_value = Counter(rss_list) # RSS

                    channel = int(bc_list[0][4]) # wlands.current_channel

                    duration = int(bc_list[0][6]) # wlan_radio.duration

                    ssid = bc_list[0][1] # wlan.ssid

                    mac_addr = bc_list[0][0] # wlan.sa
                    
                    csv_fm = filePath.beacon_path + key + "/" + key + "_FeatureModle.csv"
                    
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

return
mac_csv_dc : key:wlan.sa, value : csv file name list
"""
def make_macCsvFile(path,mac_list,m_interval):
    mac_csv_dc = {}
    csv_nameList = []

    for mac_name in mac_list: #Set key: wlan.sa, value : empty list
        mac_csv_dc.update({mac_name:[]})
    
    for mac_name in mac_list:   #make csv file names
        for hour in range(0,24,1):
            for minute in range(0,60,m_interval):
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