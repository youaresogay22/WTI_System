"""
title : Wireless terminal identification system
author : 김용환 (yh.kim951107@gmail.com)
date : 2020-08-03
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
import identify
import collect
import testset
import probe
import beacon

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
    collect.device_filter_testcase(filePath.learn_csv_probe_path,mode="probe",train=True)

    # 맥주소 추출
    mac_list = prePro.extract_macAddress(filePath.learn_csv_probe_path)   

    # 맥주소 오름차순 정렬
    mac_list.sort()

    #probe.csv 파일 읽기
    data = probe.read_probe(filePath.learn_csv_probe_path) 

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
    
    # 학습 데이터 생성
    # feat_x_train : [[delta seq no, length], ..., [...]]
    # feat_y_train : [0,0,1,1, ..., 2]
    feat_x_train, feat_y_train = machine_learn.get_proReq_train_data(fm_name_list) 

    # 무선단말 식별 모델 생성
    device_model = machine_learn.random_forest_model(feat_x_train,feat_y_train)
    
    # 무선단말 식별 모델 저장
    machine_learn.save_model(device_model,"device_model.pkl")

    # 무선단말 식별 레이블 딕셔너리 저장
    machine_learn.save_label_dic(device_dic,"device_label.json")

"""becon-frame 가공
becon-frame을 전처리 및 가공하여 학습 모델 생성
"""
def beacon_process():
    bc_mac_list = []    # 맥주소 리스트
    bc_mac_pkt_dc = {}  # key: wlan.sa , value: becon-frame(2-D list)
    bc_mac_csv_dc = {}  # key: wlan.sa, value: csv file names(list)
    bc_csv_fm_list = [] # becon-frame feature csv file names(list)
    ap_dic = {}         # key : (ssid,MAC Address), value: label
    
    # 지정한 ap 기기만 필터하여 beacon.csv에 저장
    collect.device_filter_testcase(filePath.learn_csv_beacon_path,mode="beacon",train=True) 

    # 맥주소 추출
    bc_mac_list = prePro.extract_macAddress(filePath.learn_csv_beacon_path)
    
    # 맥주소 정렬
    bc_mac_list.sort() 

    # beacon 디렉토리 생성
    file.make_Directory(filePath.beacon_path)

    # 맥주소별 디렉토리 생성
    file.make_macDirectory(filePath.beacon_path,bc_mac_list) 

    #time별 csv파일 생성, 3분간격으로 csv파일 생성
    bc_mac_csv_dc = file.make_macCsvFile(filePath.beacon_path,bc_mac_list,3)

    # 맥별 becon-frame 데이터 추출
    bc_mac_pkt_dc = prePro.extract_packetLine(filePath.learn_csv_beacon_path,bc_mac_list)

    # time별 csv파일에 데이터 저장
    file.save_csvFile(filePath.beacon_path,bc_mac_pkt_dc,3) 

    # wlan.fixed.timestamp 전처리
    prePro.beacon_prepro(bc_mac_csv_dc) 

    # featuremodel.csv 파일 생성
    for mac_name in bc_mac_list:
        file.make_csvFeature(filePath.beacon_path,mac_name,frame="beacon")

    #bc_csv_fm_list = file.init_beacon_FeatureFile(bc_mac_csv_dc) # featuremodel.csv파일에 데이터 저장
    # featuremodel.csv파일에 특징 데이터 저장
    bc_csv_fm_list = file.init_beacon_FeatureFile(bc_mac_csv_dc) 

    # 학습데이터 생성
    # x_train : [[clock skew, rss, channel, ssid, wlan.sa], ..., [...]]
    # y_train : [[ssid, wlan.sa], ..., [...]]
    # ap_dic : "label" : [ssid, wlan.sa], ex) "0" : ["carlynne","ff:ff:ff:ff:ff:ff"]
    x_train, y_train, ap_dic = machine_learn.get_becon_train_data(bc_csv_fm_list) 
    
    # AP식별 모델 생성
    ap_model = machine_learn.random_forest_model(x_train,y_train)
    
    # AP식별 모델 저장
    machine_learn.save_model(ap_model,"ap_model.pkl")

    # AP식별 레이블 딕셔너리 저장    
    machine_learn.save_label_dic(ap_dic,"ap_label.json")
    
def main():
    while True:
        cmd_num = input("input the command\n"
                        +"1: init directory\n"
                        +"2: collect the packet\n"
                        +"3: filter the pcapng file\n"
                        +"4: training the ap/device\n"
                        +"5: create test set\n"
                        +"6: test the probe-request\n"
                        +"7: exit\n")

        if cmd_num=="1": #디렉토리를 초기화한다.
            file.init_directory()

        elif cmd_num=="2": #패킷 데이터를 수집한다.
            temp = input("input the network interface, duration, pcapname('wlan1' 3600 data.pcapng) : ").split(" ")
            neti, duration, pcapng_name = temp[0], temp[1], temp[2] #네트워크인터페이스, 수집time, 저장파일이름
            collect.packet_collect(neti, duration, pcapng_name=pcapng_name)
            
        elif cmd_num=="3": #pcapng 파일을 필터링한다.
            #필터링할 pcapng 파일 리스트를 출력한다.
            print(".pcapng file list")
            os.system("ls {} | grep '.*[.]pcapng'".format(filePath.pf_path))
            pcapng_name = input("input the file name to filter the pcapng file(data.pcpapng) : ")
            pcapng_path = filePath.pf_path +"/"+ pcapng_name

            # pcapng 파일을 필터링한다.
            collect.packet_filter(pcapng_path,csv_beacon_name=filePath.learn_csv_beacon_path,
                                    csv_probe_name=filePath.learn_csv_probe_path, filter="all") #convert the pcapng file to csv file                            

        elif cmd_num=="4": #학습용 데이터를 가공한다.
            proReq_process() # probe-request 가공
            beacon_process() # becon-frame 가공 및 학습 모델 생성

            #무선 및 AP 식별 모델 불러오기
            ap_model = machine_learn.load_model("ap_model.pkl")
            ap_dic = machine_learn.load_label_dic("ap_label.json")
            device_model = machine_learn.load_model("device_model.pkl")
            device_dic = machine_learn.load_label_dic("device_label.json")
        
        elif cmd_num=="5": #테스트용 데이터를 가공한다.
            #필터링할 pcapng 파일 리스트 출력
            print(".pcapng file list")
            os.system("ls {} | grep '.*[.]pcapng'".format(filePath.pf_path))
            pcapng_name = input("input the file name to filter the pcapng file(data.pcpapng) : ")
            pcapng_path = filePath.pf_path +"/"+ pcapng_name

            #pcapng 파일 필터링
            collect.packet_filter(pcapng_path,csv_beacon_name=filePath.test_csv_beacon_path,
                                    csv_probe_name=filePath.test_csv_probe_path, filter="all") #convert the pcapng file to csv file                            


            # Probe-request 테스트 데이터 가공 및 생성
            proReq_input = testset.proReq_createTestset() 
            
            # Probe-request 테스트 데이터 저장
            with open(filePath.packet_test_probe_csv_path,"w") as f:
                writer = csv.writer(f)
                writer.writerows(proReq_input)
            
            # beacon-frame 테스트 데이터 생성
            beacon_input = testset.beacon_createTestset() 

            # 테스트 데이터 저장
            with open(filePath.packet_test_beacon_csv_path,"w") as f:
                writer = csv.writer(f)
                writer.writerows(beacon_input)
            
        elif cmd_num=="6":#테스트용 데이터를 학습 모델에 넣어 식별결과를 확인한다.
            #무선 식별 학습 모델 불러오기
            device_model = machine_learn.load_model("device_model.pkl")
            device_dic = machine_learn.load_label_dic("device_label.json")
            proReq_input = []
            y_test = []
            
            # probe-request 테스트 데이터 참조
            with open(filePath.packet_test_probe_csv_path,"r") as f:
                rdr = csv.reader(f)
                for line in rdr:
                    proReq_input.append(line[:3])  # [[delta seq no, length], ...]
                    y_test.append(int(line[-1]))    # [label]
                    

            # probe-request 테스트 데이터 평가
            testset.packet_probe_test(device_model,device_dic,proReq_input,y_test)
            
            # AP 식별 모델 불러오기
            ap_model = machine_learn.load_model("ap_model.pkl")
            ap_dic = machine_learn.load_label_dic("ap_label.json")
            beacon_input = []
            bc_y_test = []
            
            # beacon-frame 테스트 데이터 참조
            with open(filePath.packet_test_beacon_csv_path,"r") as f:
                rdr = csv.reader(f)
                for line in rdr:
                    beacon_input.append(line[:-1])  # [[clock skew, channel, rss, duration, ssid, mac address]...[...]] 
                    bc_y_test.append(int(line[-1])) # [label]
                    
            # AP 식별 모델에 테스트용 데이터를 넣어서 식별결과를 확인한다.
            testset.packet_beacon_test(ap_model, ap_dic, beacon_input, bc_y_test)
            
        elif cmd_num=="7": #프로그램 종료
            return;
        else:
            print("This is an invalid the command!!")

if __name__=="__main__":
    main()



