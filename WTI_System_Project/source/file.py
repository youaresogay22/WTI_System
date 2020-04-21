import os
import csv
import timeTrans
import delSeqNum
import filePath



#probe 폴더 생성
def make_probeDirectory():
    #맥 어드레스 별로 디렉토리 생성
    if not os.path.exists(filePath.probe_path):
        os.mkdir(filePath.probe_path)
        print("Directory ",filePath.probe_path," created")
    else:
        print("Directory ",filePath.probe_path," already exist")

#mac 폴더 생성
def make_macDirectory(mac_list):
    for idx in range(len(mac_list)):
        if not os.path.exists(filePath.probe_path+mac_list[idx]):
            os.mkdir(filePath.probe_path+mac_list[idx])
            print("Directory ",filePath.probe_path,mac_list[idx], " created")
        else:
            print("Directory ",filePath.probe_path,mac_list[idx], " already exist")

#시간별 csv파일 생성 및 딕셔너리에 csv파일 이름 리스트 저장
def make_csvFile(mac_list, mac_csv_dc):
    csv_nameList = []

       #시간별 csv 파일 생성
    for idx in range(len(mac_list)):
        #시, 분 별 csv 파일 이름 생성
        for hour in range(0,24,1):
            for minute in range(0,60,10):
                csv_filename = filePath.probe_path+mac_list[idx]+"/" + mac_list[idx] + "_" + str(hour) + "_" + str(minute) + ".csv"
                csv_nameList.append(csv_filename)

                #mac키에 csv파일 이름 추가
                mac_csv_dc[mac_list[idx]].append(csv_filename)
        
        #시간별 csv 파일 생성
        for csvName in csv_nameList:
            with open(csvName,"w") as f:
                csv.writer(f)
    
    return mac_csv_dc

#mac별 시퀀스넘버증가량,길이(length),레이블 Feature 모델 csv파일 생성
def make_csvFeature(mac):
    csvFeatureFileName = filePath.probe_path+mac+"/"+mac+"_"+"FeatureModle.csv"
    with open(csvFeatureFileName,"w") as f:
        writer = csv.writer(f)
        writer.writerow(["delta seq no","length","label"])

#시간별로 csv파일에 저장
def save_csvFile(mac_list,mac_dc):
 
    #딕셔너리 k값 순회
    for k in mac_dc.keys():
        value = mac_dc[k]   #딕셔너리 키값에 대한 값(2차원 리스트) 저장

        #리스트들 순회
        for i in range(len(value)):
            second = int(float(value[i][1]))
            h, m = timeTrans.trans_time(second) # 패킷 데이터의 경과된 시, 분 변환
            
            csv_filename = filePath.probe_path + k + "/" + k + "_" + str(h) + "_" + str(m) +".csv" #csv 파일 이름 생성
            
            
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
                W = delSeqNum.linear_regreesion(time_list,seqNum_list)

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