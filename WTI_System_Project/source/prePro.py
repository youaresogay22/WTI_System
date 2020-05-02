import csv
import extract
import copy
import filePath
import pandas as pd
from pandas import DataFrame
import math

#시퀀스번호 전처리
def preReq_Prepro():
    seq_list = []               #시퀀스번호를 저장할 리스트
    seq_temp_list = []    #가공된 시퀀스 번호를 저장할 임시 리스트
    length_list = []          #패킷 길이 리스트
    ssid_list = []              #ssid 리스트
    cycle=0             #사이클

    #csv 파일 오픈
    csv_file = pd.read_csv(filePath.csv_probe_path)
    seq_list = list(csv_file["wlan.seq"])
    length_list = list(csv_file["frame.len"])
    ssid_list = list(csv_file["wlan.ssid"])
    seq_temp_list = copy.deepcopy(seq_list)
    
    #반복문을 통하여 시퀀스번호, 길이를 가공
    for idx in range(len(seq_list)):
        if idx!=0 and int(seq_list[idx])<int(seq_list[idx-1]):
            cycle = cycle + 1
        seq_temp_list[idx] = int(seq_list[idx]) + (cycle*4096)

        #ssid가 존재하면 패킷 길이에서 ssid를 뺀다.
        if type(ssid_list[idx]) is str:
            length_list[idx] = int(length_list[idx]) - len(ssid_list[idx])

    #seq_list에 복사
    seq_list = copy.deepcopy(seq_temp_list)
    csv_file["wlan.seq"] = seq_list
    csv_file["frame.len"] = length_list
    
    #csv 작성
    data_df = DataFrame(csv_file)
    data_df.to_csv(filePath.csv_probeRe_path,sep=",",na_rep="NaN",index=False)

def beacon_prepro():
    time_list = []               #시퀀스번호를 저장할 리스트
    ts_0 = 0

    csv_file = pd.read_csv(filePath.csv_beacon_path)
    time_list = list(csv_file["wlan.fixed.timestamp"])
    
    ts_0 = time_list[0]
    
    for t_i in time_list:
        print(t_i)
    #ts_list = [(t_i - ts_0) for t_i in time_list]
    #print(ts_list)