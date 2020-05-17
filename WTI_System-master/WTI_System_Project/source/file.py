import os
import csv
import timeTrans
import delSeqNum
import filePath




#probe 폴더 생성
def make_Directory(path):
    os.system("sudo rm -r "+path)

    #맥 어드레스 별로 디렉토리 생성
    if not os.path.exists(path):
        os.mkdir(path)
        print("Directory ",path," created")
    else:
        print("Directory ",path," already exist")

#mac 폴더 생성
def make_macDirectory(path,mac_list):
    for mac_name in mac_list:
        if not os.path.exists(path+mac_name):
            os.mkdir(path+mac_name)
            print("Directory ",path,mac_name, " created")
        else:
            print("Directory ",path,mac_name, " already exist")

#mac별 시퀀스넘버증가량,길이(length),레이블 Feature 모델 csv파일 생성
def make_csvFeature(path,mac,frame="seq"):
    csvFeatureFileName = path+mac+"/"+mac+"_"+"FeatureModle.csv"
    with open(csvFeatureFileName,"w") as f:
        writer = csv.writer(f)
        if frame=="seq":
            writer.writerow(["delta seq no","length","label"])
        elif frame=="beacon":
            writer.writerow(["Clock skew","RSS","ch1","ch2","ch3","ch4","ch5","ch6","ch7","ch8","ch9","duration","SSID","MAC Address"])

#시간별로 csv파일에 저장
def save_csvFile(path,mac_dc,interval):
    col = 1
    if interval==10:
        col = 1
    elif interval==3:
        col = 3

    #딕셔너리 k값 순회
    for k in mac_dc.keys():
        value = mac_dc[k]   #딕셔너리 키값에 대한 값(2차원 리스트) 저장

        #리스트들 순회
        for i in range(len(value)):
            second = int(float(value[i][col]))
            h, m = timeTrans.trans_time(second,interval) # 패킷 데이터의 경과된 시, 분 변환
            
            csv_filename = path + k + "/" + k + "_" + str(h) + "_" + str(m) +".csv" #csv 파일 이름 생성
            
            
            #csv 파일 내용 작성
            with open(csv_filename,"a") as f:
                writer = csv.writer(f)
                writer.writerow(value[i])

#Feature 추출 모델에 데이터 입력
def init_seq_FeatureFile(mac_csv_dc):
    time_list = []          #수신시간 리스트
    seqNum_list = []    #시퀀스넘버 리스트
    W = 0                     #기울기
    label = 0                 #무선단말 레이블

    for key,value in mac_csv_dc.items():

        #시간별 csv파일을 참조하여 시퀀스 넘버 증가량, 길이, label 설정
        for idx in range(len(value)):
            csvFile = value[idx]           
            time_list = delSeqNum.make_timeRelative_list(csvFile)
            seqNum_list = delSeqNum.make_seqNumberList(csvFile)
            
            if not time_list or not seqNum_list:
                continue
            else:
                #시퀀스 넘버 기울기를 구하는 머신러닝 생성
                W = float(delSeqNum.linear_regreesion(time_list,seqNum_list))
            
            #Feature 추출 모델 이름 생성
            csv_fm = filePath.probe_path + key + "/" + key + "_FeatureModle.csv"

            #길이 저장
            with open(csvFile,"r") as f:
                rdr = csv.reader(f)
                length = rdr.__next__()[4]
            
            with open(csv_fm,"a") as f:
                feature_lline = [W,length,label]
                writer = csv.writer(f)
                writer.writerow(feature_lline)
            
            label += 1
#beacon frame value 초기화
def init_beacon_FeatureFile(bc_mac_csv_dc):
    bc_list = []
    x_train = []
    y_train = []
    rss_list = []
    rss_value=0
    ch_list = [0 for _ in range(1,10)]
    ch_val = 0
    duration = 0
    ssid = ""
    mac_addr = ""
    for key, value in bc_mac_csv_dc.items():
        for idx in range(len(value)):
                csvFile = value[idx]
                
                #csv파일에 있는 패킷 데이터 라인 리스트에 복사
                with open(csvFile,"r") as f:
                    rdr = csv.reader(f)
                    for line in rdr:
                        bc_list.append(line)
                
                #리스트가 비었으면 continue
                if not bc_list:
                    continue
                else:
                    
                    for idx in range(len(bc_list)):
                        x_train.append([float(bc_list[idx][2])])
                        y_train.append([(float(bc_list[idx][3])-float(bc_list[0][3]))-float(bc_list[idx][2])])
                        rss_list.append(int(bc_list[idx][5]))
                if x_train and y_train:
                    #clock sycle
                    W = float(delSeqNum.linear_regreesion(x_train,y_train))
                    
                    #RSS
                    rss_value = Counter(rss_list)
                    
                    #채널
                    ch_val = int(bc_list[0][4])
                    ch_list[ch_val-1] = 1

                    #duration
                    duration = int(bc_list[0][6])

                    #ssid
                    ssid = bc_list[0][1]

                    #mac addr
                    mac_addr = bc_list[0][0]
                    
                    #Feature 추출 모델 이름 생성
                    csv_fm = filePath.beacon_path + key + "/" + key + "_FeatureModle.csv"
                    with open(csv_fm,"a") as f:
                        feature_lline = [W,rss_value,ch_list[0],ch_list[1],ch_list[2],ch_list[3],ch_list[4],ch_list[5],ch_list[6],ch_list[7],ch_list[8],duration,ssid,mac_addr]
                        writer = csv.writer(f)
                        writer.writerow(feature_lline)
                    
                x_train = []
                y_train = []
                bc_list = []
                rss_list = []
                ch_list= [0 for _ in range(1,10)]
#최빈값 탐색
def Counter(x):
    dictionary = {}
    result = 0
    for i in x:
        if dictionary.get(i) is None:
            dictionary[i] = 1
        else:
            dictionary[i] +=1
    most = max(dictionary.values())
    for key, value in dictionary.items():
        if value == most:
                result = key
    return result