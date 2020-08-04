"""
title : preprocessor about frame
author : YONG HWAN KIM (yh.kim951107@gmail.com)
date : 2020-07-15
detail : 
todo :
"""

import csv
import copy
import filePath
import pandas as pd
import math
import os
from pandas import DataFrame

"""시퀀스 넘버 전처리
probe.csv파일을 참조하여 mac별로 시퀀스 넘버를 전처리한다.
0~4096 사이클을 연속적으로 바꾼다. (0~)
가공된 데이터를 probe_re.csv 파일에 저장한다. 

params
probe_name : 참조할 probe.csv 八日
probeRe_name : 시퀀스 넘버를 전처리한 후 저장할 probe.csv 파일
"""
def prepro_seq(probe_name, probeRe_name):
    dev_list = []
    file_list = [probe_name]
    df_list = []

    #probe.csv파일을 읽는다.
    for i in file_list:
        df = pd.read_csv(i,error_bad_lines=False)
        df = df.fillna("")
        df_list.append(df)

    data = df_list[0]
    mac_list = list(set(data["wlan.sa"]))
    
    dev_list = copy.deepcopy(mac_list)
    dummy = 0

    os.system("sudo rm -rf "+probeRe_name)
    
    for _sa in dev_list:    
        dummy = data[data["wlan.sa"] == _sa]

        indd = []
        timedif = []
        leng = []
        seqno = []
        for i in range(len(dummy)):
            if i != 0 and dummy.iloc[i]["wlan.seq"] - dummy.iloc[i-1]["wlan.seq"] < 0:
                indd.append(i)

            timedif.append(dummy.iloc[i]["frame.time_relative"] - dummy.iloc[0]["frame.time_relative"])
            leng.append(dummy.iloc[i]["frame.len"] - len(dummy.iloc[i]["wlan.ssid"]))

        for i in range(len(indd)):
            if i == len(indd) - 1:
                dummy.iloc[indd[i]:]["wlan.seq"] = dummy.iloc[indd[i]:]["wlan.seq"] + 4096 * (i+1)
            else:
                dummy.iloc[indd[i]:indd[i+1]]["wlan.seq"] = dummy.iloc[indd[i]:indd[i+1]]["wlan.seq"] + 4096 * (i+1)

        for i in range(len(dummy)):
            seqno.append(dummy.iloc[i]["wlan.seq"] - dummy.iloc[0]["wlan.seq"])     

        newdummy = pd.DataFrame({'sa' : dummy["wlan.sa"], 'timedifference':timedif, 'sequence no':seqno, 'length':leng})

        newdummy.to_csv(probeRe_name,mode="a",header=False,index=False)
  
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

"""맥주소 추출

params
path : 파일 이름

return
중복되지 않는 맥주소 리스트
"""
def extract_macAddress(path):
    csv_file = pd.read_csv(path)
    mac_list = list(set(csv_file["wlan.sa"])) #unique and list
    mac_list.sort()
    return mac_list