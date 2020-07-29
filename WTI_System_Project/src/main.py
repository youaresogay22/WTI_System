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
import identify
import collect
import testset
import probe


"""probe-request 가공
probe-request를 전처리 및 학습 모델 생성
"""
def proReq_process():
    mac_list = []       # wlan.sa list, list["fe:e6:1a:f1:d6:49", ... ,"f4:42:8f:56:be:89"]
    feat_x_train = []   # random forest model x_train
    feat_y_train = []   # random forest model y_train
    device_dic = {}     # key:label value: mac address
    label = 0

    collect.device_filter(filePath.learn_csv_probe_path) # 지정한 기기만 필터하여 probe.csv에 저장

    mac_list = prePro.extract_macAddress(filePath.learn_csv_probe_path)   # 맥주소 추출

    data = probe.read_probe(filePath.learn_csv_probe_path)

    probe.separate_probe(mac_list,data)

    # make feature csv file for each the wlan.sa
    for mac_name in mac_list:
        file.make_csvFeature(filePath.probe_path,mac_name,"seq")

    for mac in mac_list:
        device_dic.update({label:mac})
        label += 1
    
    fm_name_list = file.init_seq_FeatureFile(data, mac_list, filePath.probe_path, device_dic) #a dd the feature data
    
    feat_x_train, feat_y_train = machine_learn.get_proReq_train_data(fm_name_list) # 학습 데이터 생성


    device_model = machine_learn.random_forest_model(feat_x_train,feat_y_train) # 무선단말 식별 모델 생성
    
    machine_learn.save_model(device_model,"device_model.pkl")

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
    
    bc_mac_list = prePro.extract_macAddress(filePath.learn_csv_beacon_path) # 맥주소 추출
    
    bc_mac_list.sort() # 맥주소 정렬

    file.make_macDirectory(filePath.beacon_path,bc_mac_list) # 맥주소별 디렉토리 생성

    bc_mac_csv_dc = file.make_macCsvFile(filePath.beacon_path,bc_mac_list,3) #time별 csv파일 생성

    bc_mac_pkt_dc = prePro.extract_packetLine(filePath.learn_csv_beacon_path,bc_mac_list) #becon-frame데이터 추출

    file.save_csvFile(filePath.beacon_path,bc_mac_pkt_dc,3) # time별 csv파일에 데이터 저장

    prePro.beacon_prepro(bc_mac_csv_dc) # wlan.fixed.timestamp 전처리

    # featuremodel.csv 파일 생성
    for mac_name in bc_mac_list:
        file.make_csvFeature(filePath.beacon_path,mac_name,frame="beacon")

    bc_csv_fm_list = file.init_beacon_FeatureFile(bc_mac_csv_dc) # featuremodel.csv파일에 데이터 저장

    x_train, y_train, ap_dic = machine_learn.get_becon_train_data(bc_csv_fm_list) # 학습데이터 생성
    
    ap_model = machine_learn.random_forest_model(x_train,y_train) # AP식별 모델 생성
    
    machine_learn.save_model(ap_model,"ap_model.pkl")
    
    machine_learn.save_label_dic(ap_dic,"ap_label.json")

"""AP scan
becon-frame 수집 후 가공 데이터로 만들어 식별 모델에 넣기 위한 데이터 형식으로 만들어 반환한다.

param
neti : network interface
1. 3분동안 becon-frame을 수집한다.
2. becon-frame을 가공한다.
3. feature record를 반환한다.

return
bc_input : [clock skew, channel, rss, duration, ssid, mac address]
"""
def ap_scan(neti):

    os.system("sudo ifconfig {} down".format(neti))
    os.system("sudo iwconfig {} mode monitor".format(neti))
    os.system("sudo ifconfig {} up".format(neti))

    os.system("sudo tshark -i {} -w ".format(neti)
                + filePath.scan_beacon_data_path
                + " -f \'wlan type mgt and (subtype beacon)\'"
                + " -a duration:{}".format("180"))

    collect.packet_filter(filePath.scan_beacon_data_path,csv_beacon_name=filePath.scan_beacon_csv_path
                            ,filter="beacon")

    bc_mac_list = []    # 맥주소 리스트
    bc_mac_pkt_dc = {}  # key: wlan.sa , value: becon-frame(2-D list)
    bc_mac_csv_dc = {}  # key: wlan.sa, value: csv file names(list)
    bc_csv_fm_list = [] # featuremodel.csv 파일 이름 리스트

    bc_mac_list = prePro.extract_macAddress(filePath.scan_beacon_csv_path) # 맥주소 추출

    file.make_macDirectory(filePath.scan_beacon_path,bc_mac_list) # 맥주소별 디렉토리 생성

    bc_mac_csv_dc = file.make_macCsvFile(filePath.scan_beacon_path,bc_mac_list,3,end_hour=1,end_min=3)

    bc_mac_pkt_dc = prePro.extract_packetLine(filePath.scan_beacon_csv_path,bc_mac_list) # 패킷 데이터 추출

    file.save_csvFile(filePath.scan_beacon_path,bc_mac_pkt_dc,3) # csv파일에 데이터 저장
    
    prePro.beacon_prepro(bc_mac_csv_dc) # wlan.fixed.timestamp 전처리

    # featuremodel.csv 파일 생성
    for mac_name in bc_mac_list:
        file.make_csvFeature(filePath.scan_beacon_path,mac_name,frame="beacon")

    # featuremodel.csv 파일에 데이터 저장
    bc_csv_fm_list = file.init_beacon_FeatureFile(bc_mac_csv_dc,becon_path=filePath.scan_beacon_path)

    x_train, y_train , ap_dic = machine_learn.get_becon_train_data(bc_csv_fm_list) #x_train : [[clock skew, channel, rss, duration, ssid, mac address]]

    beacon_input = []
    for x, y in zip(x_train, y_train):
        list1 = x
        list2 = ap_dic[y]
        beacon_input.append(list1+list2) #[[clock skew, channel, rss, duration, ssid, mac address]..[...]]
    
    return beacon_input

def main():
    while True:
        cmd_num = input("input the command\n"
                        +"1: init directory\n"
                        +"2: collect the packet\n"
                        +"3: filter the pcapng file\n"
                        +"4: training the ap/device\n"
                        +"5: ap scan\n"
                        +"6: device scan\n"
                        +"7: exit\n"
                        +"8: create test set\n"
                        +"9: test the probe-request\n")

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
            beacon_process() # becon-frame 가공 및 학습 모델 생성
            ap_model = machine_learn.load_model("ap_model.pkl")
            ap_dic = machine_learn.load_label_dic("ap_label.json")
            device_model = machine_learn.load_model("device_model.pkl")
            device_dic = machine_learn.load_label_dic("device_label.json")
            
        elif cmd_num=="5":
            while True:
                beacon_input = ap_scan("wlan1")
                identify.ap_identify(ap_model,ap_dic,beacon_input)
        elif cmd_num=="6":
            print("device scan!!")
        elif cmd_num=="7":
            return;
        elif cmd_num=="8":
            print(".pcapng file list")
            os.system("ls {} | grep '.*[.]pcapng'".format(filePath.pf_path))
            pcapng_name = input("input the file name to filter the pcapng file(data.pcpapng) : ")
            pcapng_path = filePath.pf_path +"/"+ pcapng_name

            collect.packet_filter(pcapng_path,csv_beacon_name=filePath.test_csv_beacon_path,
                                    csv_probe_name=filePath.test_csv_probe_path, filter="all") #convert the pcapng file to csv file                            


            proReq_input = testset.proReq_createTestset() # 테스트 데이터 생성
            
            # 테스트 데이터 저장
            with open(filePath.packet_test_probe_csv_path,"w") as f:
                writer = csv.writer(f)
                writer.writerows(proReq_input)

            beacon_input = testset.beacon_createTestset() # 테스트 데이터 생성

            # 테스트 데이터 저장
            with open(filePath.packet_test_beacon_csv_path,"w") as f:
                writer = csv.writer(f)
                writer.writerows(beacon_input)

        elif cmd_num=="9":
            device_model = machine_learn.load_model("device_model.pkl")
            device_dic = machine_learn.load_label_dic("device_label.json")
            proReq_input = []
            y_test = []

            # 테스트 데이터 참조
            with open(filePath.packet_test_probe_csv_path,"r") as f:
                rdr = csv.reader(f)
                for line in rdr:
                    proReq_input.append(line[:-1])  # [[delta seq no, length], ...]
                    y_test.append(int(line[-1]))    # [label]

            # 테스트 데이터 평가
            testset.packet_test(device_model,device_dic,proReq_input,y_test)

            ap_model = machine_learn.load_model("ap_model.pkl")
            ap_dic = machine_learn.load_label_dic("ap_label.json")
            beacon_input = []
            bc_y_test = []
            # 테스트 데이터 참조
            with open(filePath.packet_test_beacon_csv_path,"r") as f:
                rdr = csv.reader(f)
                for line in rdr:
                    beacon_input.append(line[:-1])  # [[clock skew, channel, rss, duration, ssid, mac address]...[...]] 
                    bc_y_test.append(int(line[-1])) # [label]
                    
            # 테스트 데이터 평가
            testset.packet_test(ap_model, ap_dic, beacon_input, bc_y_test)
            
        else:
            print("This is an invalid the command!!")

if __name__=="__main__":
    main()



