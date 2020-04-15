import csv
import macPro
import copy

csv_file_path = "/home/user/Desktop/git/WTI_System_Project/csv/"

#맥 어드레스 추출
def extract_macAddress():
    with open(csv_file_path+"probe_re.csv","r") as f:
        rdr = csv.reader(f)
        mac_list = extract_data_header(rdr,"wlan.sa")   #맥 추출
        mac_list = list(set(mac_list))  #맥 중복 제거
    return mac_list

# csv 열 데이터 추출
def extract_data_header(rdr, header):
    list = []
    rdr_header = next(rdr)  #csv파일의 헤더
    idx = 0                            #추출할 인덱스 열 번호    
        
    # 추출할 인덱스 열 번호 탐색
    for i in range(len(rdr_header)):
        if rdr_header[i] == header:
            idx = i
            break  
        
    # 열 데이터 추출
    for line in rdr:
        list.append(line[idx])

    return list

#csv 열 데이터 추출
def extract_data_index(rdr,idx):
    list = []
    for line in rdr:
        list.append(line[idx])
    return list

#패킷 라인 추출
def extract_packetLine(mac_list,mac_dc):
    with open(csv_file_path+"probe_re.csv","r") as f:
        rdr = csv.reader(f)
        packet_list=[]

        #rdr을 packet_list으로 복사
        for line in rdr:
            packet_list.append(line);

        for idx in range(len(mac_list)):
            #패킷데이터의 해당 단말의 mac이면 리스트에 저장한다.
            for line in packet_list:
                if line[0]==mac_list[idx]:
                    mac_dc[mac_list[idx]].append(line)

    
    return mac_dc