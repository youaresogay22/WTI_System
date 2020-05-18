import csv
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

#beacon frame 전처리
def beacon_prepro(bc_mac_pkt_dc):
    pkt_list = []
    time_zero = 0
    for key in bc_mac_pkt_dc.keys():
            pkt_list = copy.deepcopy(bc_mac_pkt_dc[key])
            time_zero = pkt_list[0][2]
            
            for idx in range(len(pkt_list)):
                pkt_list[idx][2] = (int(pkt_list[idx][2]) - int(time_zero))/1000000
            
            bc_mac_pkt_dc[key] = copy.deepcopy(pkt_list)    

    return bc_mac_pkt_dc


#초를 입력받아 시간과 분으로 반환한다.
def trans_time(second,interval):
    #시간, 분 계산
    sec = second

    h = int(sec // 3600)
    sec = int(sec%3600)

    m = int(sec//60)
    m = (m//interval)*interval
    
    return str(h), str(m)


#맥 어드레스 추출
def extract_macAddress(path):
    csv_file = pd.read_csv(path)
    return list(set(csv_file["wlan.sa"]))
    

#csv 열 데이터 추출
def extract_data_index(rdr,idx):
    list = []
    for line in rdr:
        list.append(line[idx])
    return list

#패킷 라인 추출
def extract_packetLine(path,mac_list):
    mac_dc = {}

    #mac별 dictionary 초기화
    for mac_name in mac_list:
        mac_dc.update({mac_name:[]})
    
    with open(path,"r") as f:
        rdr = csv.reader(f)
        packet_list=[]

        #rdr을 packet_list으로 복사
        for line in rdr:
            packet_list.append(line);

        for mac_name in mac_list:
            #패킷데이터의 해당 단말의 mac이면 리스트에 저장한다.
            for line in packet_list:
                if line[0]==mac_name:
                    mac_dc[mac_name].append(line)
    
    return mac_dc