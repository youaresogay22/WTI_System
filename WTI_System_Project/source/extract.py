import csv
import macPro
import copy
import filePath
import pandas as pd



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