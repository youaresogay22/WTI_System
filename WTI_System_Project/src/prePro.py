"""
title : preprocessor about frame
author : YONG HWAN KIM (yh.kim951107@gmail.com)
date : 2020-08-03
detail : 
todo :
"""

import pandas as pd
import csv
import copy

"""맥주소 추출
params
path : 파일 이름

return
mac_list : 중복되지 않는 맥주소 리스트
"""
def extract_macAddress(path):
    csv_file = pd.read_csv(path)
    mac_list = list(set(csv_file["wlan.sa"])) #unique and list
    mac_list.sort()
    return mac_list


"""패킷 데이터 추출
params
path : 추출하고자 하는 파일
mac_list : wlan.sa (맥주소) 리스트

return
mac_dc : key:wlan.sa value: packet
"""
def extract_packetLine(path,mac_list):
    mac_dc = {}

    for mac_name in mac_list:   # dictionary 초기화
        mac_dc.update({mac_name:[]})
    
    with open(path,"r") as f:
        rdr = csv.reader(f)
        packet_list=[]

        #데이터 추출
        for line in rdr:
            packet_list.append(line);

        #맥별 패킷 분류
        for mac_name in mac_list: 
            for line in packet_list:
                if line[0]==mac_name:
                    mac_dc[mac_name].append(line)
    
    return mac_dc

"""비콘 프레임 전처리
wlan.fixed.timestamp 데이터 전처리한다.
시간별 파일을 참조하여 wlan.fixed.timestamp의 timedifference(t_i - t_0)을 구하여 저장한다.

params
bc_mac_csv_dc : key:wlan.sa(맥주소), value: csv 파일 이름들
"""
def beacon_prepro(bc_mac_csv_dc):
    csv_list = []   #csv 시간 파일 이름 리스트
    bc_list=[]      #becon-frame 데이터 리스트
    time_zero = 0   #0th wlan.fixed.timestamp

    for key in bc_mac_csv_dc.keys():        
        csv_list = copy.deepcopy(bc_mac_csv_dc[key])
        
        for csv_file in csv_list:
            
            with open(csv_file,"r") as f:
                rdr = csv.reader(f)

                #0번째 timestamp 전처리
                try:
                    line = next(rdr)
                    time_zero = line[2]                                 #timestamp 저장
                    line[2] = (int(line[2]) - int(time_zero))/1000000   #timestamp 전처리
                    bc_list.append(line)                                #전처리된 becon-frame 리스트에 추가
                except:
                    continue

                #becon-frame timestamp 전처리
                for line in rdr:
                    line[2] = (int(line[2]) - int(time_zero))/1000000
                    bc_list.append(line)

            with open(csv_file,"w") as f:
                writer = csv.writer(f)
                writer.writerows(bc_list) 
            bc_list = []

"""시간변환
sec와 interval을 입력으로 얻어서 시,분으로 변환한다.

params
sec : second
interval : probe-request => 10, becon-frame => 3

return
hour, minute
"""
def trans_time(sec,interval):
    s = sec

    h = int(s // 3600)
    s = int(s%3600)

    m = int(s//60)
    m = (m//interval)*interval
    
    if h<10:
        h = "0"+str(h)
    if m<10:
        m = "0"+str(m)

    return str(h), str(m)
