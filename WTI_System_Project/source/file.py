import os
import csv
import timeTrans

probe_path = "/home/user/Desktop/git/WTI_System_Project/probe/"

#probe 폴더 생성
def make_probeDirectory():
    #맥 어드레스 별로 디렉토리 생성
    if not os.path.exists(probe_path):
        os.mkdir(probe_path)
        print("Directory ",probe_path," created")
    else:
        print("Directory ",probe_path," already exist")

#mac 폴더 생성
def make_macDirectory(mac_list):
    for idx in range(len(mac_list)):
        if not os.path.exists(probe_path+mac_list[idx]):
            os.mkdir(probe_path+mac_list[idx])
            print("Directory ",probe_path,mac_list[idx], " created")
        else:
            print("Directory ",probe_path,mac_list[idx], " already exist")

#시간별 csv파일 생성 및 딕셔너리에 csv파일 이름 리스트 저장
def make_csvFile(mac_list, mac_csv_dc):
    csv_nameList = []

       #시간별 csv 파일 생성
    for idx in range(len(mac_list)):
        #시, 분 별 csv 파일 이름 생성
        for hour in range(0,24,1):
            for minute in range(0,60,10):
                csv_filename = probe_path+mac_list[idx]+"/" + mac_list[idx] + "_" + str(hour) + "_" + str(minute) + ".csv"
                csv_nameList.append(csv_filename)

                #mac키에 csv파일 이름 추가
                mac_csv_dc[mac_list[idx]].append(csv_filename)
        
        #시간별 csv 파일 생성
        for csvName in csv_nameList:
            with open(csvName,"w") as f:
                csv.writer(f)
    
    return mac_csv_dc


#시간별로 csv파일에 저장
def save_csvFile(mac_list,mac_dc):
 
    #딕셔너리 k값 순회
    for k in mac_dc.keys():
        value = mac_dc[k]   #딕셔너리 키값에 대한 값(2차원 리스트) 저장

        #리스트들 순회
        for i in range(len(value)):
            second = int(float(value[i][1]))
            h, m = timeTrans.trans_time(second) # 패킷 데이터의 경과된 시, 분 변환
            
            csv_filename = probe_path + k + "/" + k + "_" + str(h) + "_" + str(m) +".csv" #csv 파일 이름 생성
            
            
            #csv 파일 내용 작성
            with open(csv_filename,"a") as f:
                writer = csv.writer(f)
                writer.writerow(value[i])