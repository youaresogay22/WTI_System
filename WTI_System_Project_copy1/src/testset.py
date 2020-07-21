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

    collect.device_filter(filePath.test_csv_probe_path) # 지정한 기기만 필터하여 probe.csv에 저장

    mac_list = prePro.extract_macAddress(filePath.test_csv_probe_path)   # 맥주소 추출

    data = probe.read_probe(filePath.test_csv_probe_path)

    probe.separate_probe(mac_list,data,csvname="probe_test")

    # make feature csv file for each the wlan.sa
    for mac_name in mac_list:
        file.make_csvFeature(filePath.probe_test_path,mac_name,"seq")

    device_dic = machine_learn.load_label_dic("device_label.json")

    fm_name_list = file.init_seq_FeatureFile(data, mac_list, filePath.probe_test_path, device_dic,csvname="probe_test") #a dd the feature data
    
    feat_x_train, feat_y_train = machine_learn.get_proReq_train_data(fm_name_list) # 학습 데이터 생성

    feat_y_train = np.reshape(feat_y_train,(-1,1)) # [0,1,2] => [[0],[1],[2]]

    #[[delta seq no, length, label]...,] 형식으로 생성
    for x, y in zip(feat_x_train, feat_y_train):
        x.extend(y)
    
    return feat_x_train

def beacon_createTestset():
    bc_mac_list = []    # 비콘 프레이별 맥주소 리스트
    bc_mac_pkt_dc = {}  # key: wlan.sa , value: becon-frame(2-D list)
    bc_mac_csv_dc = {}  # key: wlan.sa, value: csv file names(list)
    bc_csv_fm_list = [] # featuremodel.csv 파일 이름 리스트
    ap_dic = {}         # key : label, value: (SSID, MAC Address)
    
    bc_mac_list = prePro.extract_macAddress(filePath.test_csv_beacon_path) # 맥주소 추출
    
    file.make_macDirectory(filePath.beacon_test_path,bc_mac_list) # 맥주소별 디렉토리 생성

    bc_mac_csv_dc = file.make_macCsvFile(filePath.beacon_test_path,bc_mac_list,3) # 3분별 csv파일 생성

    bc_mac_pkt_dc = prePro.extract_packetLine(filePath.test_csv_beacon_path,bc_mac_list) #비콘 프레임 데이터 추출

    file.save_csvFile(filePath.beacon_test_path,bc_mac_pkt_dc,3) # csv파일에 데이터 저장

    prePro.beacon_prepro(bc_mac_csv_dc) # wlan.fixed.timestamp 전처리

    # featuremodel.csv 파일 생성
    for mac_name in bc_mac_list:
        file.make_csvFeature(filePath.beacon_test_path,mac_name,frame="beacon")

    # featuremodel.csv 파일에 데이터 입력
    bc_csv_fm_list = file.init_beacon_FeatureFile(bc_mac_csv_dc,becon_path=filePath.beacon_test_path)

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
def packet_test(model,dic,x_input,y_test):
    y_test = np.array(y_test)
    y_pred = model.predict(x_input)

    print("y_pred : ", y_pred)
    print("y_test : ", y_test)
    print("accuracy score : ", metrics.accuracy_score(y_pred,y_test))
    print(classification_report(y_pred,y_test))

