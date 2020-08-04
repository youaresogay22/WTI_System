"""
title : 패킷 수집 및 필터링 관련 모듈
author : 김용환 (dragonbead95@naver.com)
date : 2020-08-03
detail : 
todo :
"""

import os
import filePath
import csv

"""패킷 데이터 수집
params
neti : 네트워크 인터페이스
sec : 수집time(초/s)
pcapng_name : 저장할 pcapng 파일 이름
"""
def packet_collect(neti, sec,pcapng_name="data.pcapng"):
    """랜카드를 모니터 모드로 설정
    """
    os.system("sudo ifconfig {} down".format(neti))
    os.system("sudo iwconfig {} mode monitor".format(neti))
    os.system("sudo ifconfig {} up".format(neti))
     
    #패킷 수집 명령어
    os.system("sudo tshark -i {} -w ".format(neti)
                    + filePath.pf_path
                    + "/" + pcapng_name
                    + " -f \'wlan type mgt and (subtype beacon or subtype probe-req)\'"
                    + " -a duration:{}".format(sec))

    
"""패킷 필터
pcapng 파일을 필터링하여 csv 파일로 변환한다.
pcapng_name : 필터링할 pcapng 파일 이름
csv_beacon_name : beacon-frame만을 필터링한 csv 파일 경로 및 이름
csv_probe_name : probe-request 만을 필터링한 csv 파일 경로 및 이름
filter : all-> beacon-frame, probe-request 모두 필터링
         probe -> probe-request만 필터링
         beacon -> beacon-frame만 필터링
"""
def packet_filter(pcapng_name, csv_beacon_name=filePath.learn_csv_beacon_path,
                     csv_probe_name=filePath.learn_csv_probe_path, filter="all"):

    #pcapng 파일을 참조하여 probe,beacon 데이터를 필터링한다.
    if filter=="all":
        os.system("sudo tshark -r "
                        + pcapng_name
                        + " -Y \"wlan.fc.type_subtype==0x0004\""
                        + " -T fields -e wlan.sa -e frame.time_relative -e wlan.seq -e wlan.ssid -e frame.len -E separator=, -E quote=n -E header=y > "
                        + csv_probe_name)
        os.system("sudo tshark -r "
                        + pcapng_name
                        + " -Y \"wlan.fc.type_subtype==0x0008\" -T fields -e wlan.sa -e wlan.ssid -e wlan.fixed.timestamp -e frame.time_relative -e wlan.ds.current_channel -e wlan_radio.signal_dbm -e wlan_radio.duration -E separator=, -E quote=n -E header=y > "
                        + csv_beacon_name)

    elif filter=="beacon":
        os.system("sudo tshark -r "
                        + pcapng_name
                        + " -Y \"wlan.fc.type_subtype==0x0008\" -T fields -e wlan.sa -e wlan.ssid -e wlan.fixed.timestamp -e frame.time_relative -e wlan.ds.current_channel -e wlan_radio.signal_dbm -e wlan_radio.duration -E separator=, -E quote=n -E header=y > "
                        + csv_beacon_name)

    elif filter=="probe":
        os.system("sudo tshark -r "
                        + pcapng_name
                        + " -Y \"wlan.fc.type_subtype==0x0004\""
                        + " -T fields -e wlan.sa -e frame.time_relative -e wlan.seq -e wlan.ssid -e frame.len -E separator=, -E quote=n -E header=y > "
                        + csv_probe_name)

"""
디바이스를 필터링하여 probe.csv or beacon.csv 파일에 재저장한다.
params
filename: 참조할 probe.csv, beacon.csv 파일 이름
savename : 필터링하여 저장된 csv 파일 이름 (선행연구 테스트 데이터 디버깅 매개변수)
mode : probe이면 무선단말기기 필터링, beacon이면 ap기기 필터링
train : True -> 학습용 False -> 테스트용
"""
def device_filter_testcase(filename,savename,mode, train=True):
    dummy = []
    dev_list = []

    #83~102 선행연구 테스트 데이터용 코드
    dev_list = [
            "2c:33:7a:2b:79:3a",
            "34:08:04:9b:31:79",
            "80:2b:f9:f1:5e:e9",
            "88:36:6c:f9:ca:76",
            "04:cf:8c:89:18:47",
            "ac:fd:ce:b0:da:79",
            "58:65:e6:70:38:be",
            "1c:f2:9a:69:bf:0b",
            "a8:2b:b9:b9:de:42",
            "0c:1c:20:0c:38:84",
            "60:36:dd:5e:d0:9e",
            "7c:38:ad:28:05:48",
            "ac:d1:b8:cb:6b:cb"
    ]
    dummy.append(["wlan.sa",
                    "frame.time_relative",
                    "wlan.seq",
                    "wlan.ssid",
                    "frame.len"])

    """
    #테스트 케이스에 사용한 무선단말 기기 정보
    dev_dic = {
        "A": "f8:e6:1a:f1:d6:49",
        "B": "84:2e:27:6b:53:df",
        "C": "00:f4:6f:9e:c6:eb",
        "D": "94:d7:71:fc:67:c9",
        "E": "ac:36:13:5b:00:45",
        "F": "18:83:31:9b:75:ad",
    }
    #테스트 케이스에 사용한 AP 정보
    ap_dev_dic = {
        "WIFI1": "88:36:6c:67:72:ec", #carlynne
        "WIFI2": "08:5d:dd:65:39:0e", #cafe wifi
        "WIFI3": "98:de:d0:c4:a2:e1", #OpenWrt
        "WIFI4": "a0:ec:f9:9f:a8:c0" #CNU WiFi 
    }
    if mode=="probe":
        if train==True: #훈련용 데이터 테스트 케이스중 무선단말 기기를 필터링한다.
            testcase = int(input("input the train's probe testcase(1~7) : "))

            if testcase==1 or testcase==3 or testcase==4 or testcase==6:
                dev_list=[
                    dev_dic["A"],
                    dev_dic["B"],
                    dev_dic["C"],
                    dev_dic["D"],
                    dev_dic["E"]
                ]
            elif testcase==2 or testcase==5:
                dev_list=[
                    dev_dic["A"],
                    dev_dic["B"],
                    dev_dic["C"],
                    dev_dic["D"]
                ]
            elif testcase==7:
                dev_list = [
                    dev_dic["A"],
                    dev_dic["B"],
                    dev_dic["C"]
                ]
            else:
                pass
        else: # 테스트 데이터 테스트 케이스중 무선단말 기기를 필터링한다.
            testcase = int(input("input the test's probe testcase(1~7) : "))
            if testcase==1 or testcase==4:
                dev_list=[
                    dev_dic["A"],
                    dev_dic["B"],
                    dev_dic["C"],
                    dev_dic["D"],
                    dev_dic["E"]
                ]
            elif testcase==2 or testcase==5:
                dev_list=[
                    dev_dic["A"],
                    dev_dic["B"],
                    dev_dic["C"],
                    dev_dic["E"],
                    dev_dic["F"]
                ]
            elif testcase==3 or testcase==6:
                dev_list=[
                    dev_dic["A"],
                    dev_dic["B"],
                    dev_dic["C"],
                    dev_dic["D"],
                    dev_dic["F"]
                ]
            elif testcase==7:
                dev_list = [
                    dev_dic["A"],
                    dev_dic["B"],
                    dev_dic["C"]
                ]
            else:
                pass

        dummy.append(["wlan.sa",
                        "frame.time_relative",
                        "wlan.seq",
                        "wlan.ssid",
                        "frame.len"])

    elif mode=="beacon":
        if train==True: #훈련용 데이터 테스트 케이스 중 AP 기기를 필터링한다.
            testcase = int(input("input the train's beacon testcase(0~7) : "))
            if testcase==0:
                dev_list = [ap_dev_dic["WIFI1"],
                            ap_dev_dic["WIFI2"]]
            elif testcase==1 or testcase==2 or testcase==3:
                dev_list = [ap_dev_dic["WIFI1"]]
            elif testcase==4 or testcase==5 or testcase==6:
                dev_list = [ap_dev_dic["WIFI2"]]
            elif testcase==7:
                testcase = input("input the train's ap(WIFI3 or WIFI4) : ")
                if testcase=="WIFI3":
                    dev_list = [ap_dev_dic["WIFI3"]]
                elif testcase=="WIFI4":
                    dev_list = [ap_dev_dic["WIFI4"]]
                else:
                    dev_list = [ap_dev_dic["WIFI3"],
                                ap_dev_dic["WIFI4"]]
            else:
                pass
        else: #test data filter
            testcase = int(input("input the test's beacon testcase(0~7) : "))
            if testcase==0:
                dev_list = [ap_dev_dic["WIFI1"],
                            ap_dev_dic["WIFI2"]]
            elif testcase==1 or testcase==2 or testcase==3:
                dev_list = [ap_dev_dic["WIFI1"]]
            elif testcase==4 or testcase==5 or testcase==6:
                dev_list = [ap_dev_dic["WIFI2"]]
            elif testcase==7:
                testcase = input("input the test's ap(WIFI3 or WIFI4) : ")
                if testcase=="WIFI3":
                    dev_list = [ap_dev_dic["WIFI3"]]
                elif testcase=="WIFI4":
                    dev_list = [ap_dev_dic["WIFI4"]]
                else:
                    dev_list = [ap_dev_dic["WIFI3"],
                                ap_dev_dic["WIFI4"]]         
            else:
                pass

        dummy.append(["wlan.sa",
                        "wlan.ssid",
                        "wlan.fixed.timestamp",
                        "frame.time_relative",
                        "wlan.ds.current_channel",
                        "wlan_radio.signal_dbm",
                        "wlan_radio.duration"])
    """

    #csv 파일을 열어 dev_list에 있는 맥주소만 dummy 리스트에 데이터를 저장
    with open(filename,"r") as f:
        rdr = csv.reader(f)
        
        for line in rdr:
            try:
                if line[1] in dev_list:
                    dummy.append([line[1],line[2],line[4],line[0],line[6]])
            except:
                continue
    
    #해당 파일(filename)에 dummy 내용을 재작성
    with open(savename,"w") as f:
        writer = csv.writer(f)
        writer.writerows(dummy)





        
