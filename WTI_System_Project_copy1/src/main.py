"""
title : Wireless terminal identification system
author : YONG HWAN KIM (yh.kim951107@gmail.com)
date : 2020-07-15
detail : 
todo :

"""

import csv
import os
import prePro
import machine_learn
import file
import filePath
import copy
import numpy as np
import collect
import probe

"""probe-request 가공
probe-request를 전처리 및 학습 모델 생성
"""
def proReq_process():
    mac_list = []       # wlan.sa list, list["fe:e6:1a:f1:d6:49", ... ,"f4:42:8f:56:be:89"]
    feat_x_train = []   # random forest model x_train
    feat_y_train = []   # random forest model y_train
    device_dic = {}     # key:label value: mac address, "0" : "ff:ff:ff:ff"
    label = 0           # 무선단말 레이블

    # 지정한 무선단말 기기만 필터하여 probe.csv에 저장
    collect.device_filter_testcase(filePath.learn_csv_probe_path,filePath.learn_csv_probe2_path,mode="probe",train=True)

    # 맥주소 추출
    mac_list = prePro.extract_macAddress(filePath.learn_csv_probe2_path)   

    # 맥주소 오름차순 정렬
    mac_list.sort()

    #probe.csv 파일 읽기
    data = probe.read_probe(filePath.learn_csv_probe2_path) 

    #probe 디렉토리 생성
    file.make_Directory(filePath.probe_path) 

    #data를 참조하여 맥별로 probe-request 데이터를 나눈다.
    probe.separate_probe(mac_list,data) 

    # 맥별로 FeatureModel.csv 파일을 생성한다.
    for mac_name in mac_list:
        file.make_csvFeature(filePath.probe_path,mac_name,"seq")

    # 맥별로 label 할당
    for mac in mac_list:
        device_dic.update({label:mac})
        label += 1
    
    # 맥별 featureModel.csv 파일에 특징 데이터(delta seq no, length, label)를 추가한다.
    fm_name_list = file.init_seq_FeatureFile(data, mac_list, filePath.probe_path, device_dic)

def main():
    while True:
        cmd_num = input("input the command\n"
                        +"1: init directory\n"
                        +"2: collect the packet\n"
                        +"3: filter the pcapng file\n"
                        +"4: training the ap/device\n"
                        +"5: exit\n")

        if cmd_num=="1":
            file.init_directory()

        elif cmd_num=="2":
            temp = input("input the network interface and duration('wlan1' 3600) : ").split(" ")
            neti, duration = temp[0], temp[1]
            collect.packet_collect(neti,duration) # collect the data

        elif cmd_num=="3":
            print(".pcapng file list")
            os.system("ls {} | grep '.*[.]pcapng'".format(filePath.pf_path))
            pcapng_name = input("input the file name to filter the pcapng file(data.pcpapng) : ")
            pcapng_path = filePath.pf_path +"/"+ pcapng_name

            collect.packet_filter(pcapng_path,csv_beacon_name=filePath.learn_csv_beacon_path,
                                    csv_probe_name=filePath.learn_csv_probe_path, filter="all") #convert the pcapng file to csv file                            
        elif cmd_num=="4":
            proReq_process() # probe-request 가공
        elif cmd_num=="5":
            return;
        else:
            print("This is an invalid the command!!")

if __name__=="__main__":
    main()



