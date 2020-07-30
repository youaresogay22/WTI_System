"""
title : Wireless terminal identification system
author : YONG HWAN KIM (yh.kim951107@gmail.com)
date : 2020-07-15
detail : 
todo :
"""

import file
import filePath
import machine_learn
import prePro
import numpy as np
import collect
import probe
import beacon

from sklearn import metrics
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report

"""무선 단말 테스트 데이터 생성

return
feat_x_train : [[delta seq no, length, label], ...]
"""
def proReq_createTestset():
    mac_list = []       # wlan.sa list, list["fe:e6:1a:f1:d6:49", ... ,"f4:42:8f:56:be:89"]
    feat_x_train = []   # random forest model x_train
    feat_y_train = []   # random forest model y_train
    device_dic = {}     # key:label value: mac address
    label = 0

    #collect.device_filter(filePath.test_csv_probe_path,mode="probe") # 지정한 기기만 필터하여 probe.csv에 저장
    collect.device_filter_testcase(filePath.test_csv_probe_path,mode="probe",train=False) # 지정한 기기만 필터하여 probe.csv에 저장

    mac_list = prePro.extract_macAddress(filePath.test_csv_probe_path)   # 맥주소 추출

    data = probe.read_probe(filePath.test_csv_probe_path)

    file.make_Directory(filePath.probe_test_path)

    probe.separate_probe(mac_list,data,csvname="probe_test")

    # make feature csv file for each the wlan.sa
    for mac_name in mac_list:
        file.make_csvFeature(filePath.probe_test_path,mac_name,"seq")

    device_dic = machine_learn.load_label_dic("device_label.json")

    fm_name_list = file.init_seq_FeatureFile(data, mac_list, filePath.probe_test_path, device_dic,csvname="probe_test") #a dd the feature data
    
    feat_x_train, feat_y_train = machine_learn.get_proReq_train_data(fm_name_list) # 학습 데이터 생성

    feat_y_train = np.reshape(feat_y_train,(-1,1)) # [0,1,2] => [[0],[1],[2]]

    ident_mac_list = []
    for item in feat_y_train:
        if str(item[0]) not in device_dic.keys():
            ident_mac_list.append("unknown terminal")
        else:
            ident_mac_list.append(device_dic[str(item[0])])

    #[[delta seq no, length, label]...,] 형식으로 생성
    for x, y, z in zip(feat_x_train, feat_y_train,ident_mac_list):
        x.extend([z])
        x.extend(y)
        

    return feat_x_train

def beacon_createTestset():
    bc_mac_list = []    # 맥주소 리스트
    bc_mac_pkt_dc = {}  # key: wlan.sa , value: becon-frame(2-D list)
    bc_mac_csv_dc = {}  # key: wlan.sa, value: csv file names(list)
    bc_csv_fm_list = [] # becon-frame feature csv file names(list)
    ap_dic = {}         # key : (ssid,MAC Address), value: label
    
    #collect.device_filter(filePath.learn_csv_beacon_path,mode="beacon") # 지정한 기기만 필터하여 probe.csv에 저장
    collect.device_filter_testcase(filePath.learn_csv_beacon_path,mode="beacon",train=False) # 지정한 기기만 필터하여 probe.csv에 저장

    bc_mac_list = prePro.extract_macAddress(filePath.learn_csv_beacon_path) # 맥주소 추출
    
    bc_mac_list.sort() # 맥주소 정렬

    data = probe.read_probe(filePath.learn_csv_beacon_path)

    beacon.separate_beacon(bc_mac_list,data)

    # featuremodel.csv 파일 생성
    for mac_name in bc_mac_list:
        file.make_csvFeature(filePath.beacon_path,mac_name,frame="beacon")

    bc_csv_fm_list = file.init_beacon_FeatureFile(data, bc_mac_list, filePath.beacon_path) # featuremodel.csv파일에 데이터 저장

    ap_label = machine_learn.load_label_dic("ap_label.json")

    x_train, y_train = machine_learn.get_becon_test_train_data(bc_csv_fm_list,ap_label) # 테스트 데이터 생성

    #[[clock skew, channel, rss, duration, ssid, mac address, label]...[...]] 형식 생성
    for x, y in zip(x_train, y_train):
        x.extend(y)

    return x_train

"""테스트 데이터 평가
params
model : 랜덤 포레스트 학습 모델
dic : probe-request -> key : label, value : wlan.sa
      becon-frame -> key : label, value : (SSID, wlan.sa)

x_input : probe-request -> [[delta seq no, length], ...]
          becon-frame -> [[[clock skew, channel, rss, duration, ssid, mac address], ...]
y_test : probe-request -> [label]
         becon-frame -> [label]
"""
def packet_test(model, dic, x_input, y_test):

    report_x_input = []
    for line in x_input:
        report_x_input.append(line[:2])

    report_y_pred = model.predict(report_x_input)
    report_y_test = y_test
    
    print("len : ",len(report_x_input))
    print("y_pred : ", report_y_pred)
    print("y_test : ", report_y_test)
    print("accuracy score : ", metrics.accuracy_score(report_y_pred,report_y_test))
    print(classification_report(report_y_pred,report_y_test))
    
    
    for i in range(len(x_input)):
        feat_x_input = np.reshape(x_input[i][:2],(1,-1))
        mac_addr = x_input[i][2]

        if mac_addr in dic.values():
            y_pred = model.predict(feat_x_input)[0]
            y_proba = max(model.predict_proba(feat_x_input)[0])

            print("Classification result : Terminal {}, Label : Terminal {}".format(y_pred,y_test[i]))
            print("Proba : {}".format(y_proba))
            
            if y_proba > 0.6 and y_pred==y_test[i]:
                print("This terminal is authroized terminal")
            else:
                print("This terminal is unauthorized terminal")
        else:
            print("Label : {}".format(y_test[i]))
            print("This terminal is unknown terminal")
        print()

    
    
    

