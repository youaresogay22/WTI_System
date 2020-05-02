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
def make_csvFeature(path,mac):
    csvFeatureFileName = path+mac+"/"+mac+"_"+"FeatureModle.csv"
    with open(csvFeatureFileName,"w") as f:
        writer = csv.writer(f)
        writer.writerow(["delta seq no","length","label"])

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
def init_FeatureFile(mac_csv_dc):
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