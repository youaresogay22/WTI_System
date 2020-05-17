import extract
import csv
import filePath
from pandas import DataFrame

def make_macCsvFile(path,mac_list,m_interval):
    mac_csv_dc = {}
    csv_nameList = []

    #mac맥 csv파일리스트 맵의 키 설정
    for mac_name in mac_list:
        mac_csv_dc.update({mac_name:[]})

    #시간별 csv 파일 생성
    for mac_name in mac_list:
        #시, 분 별 csv 파일 이름 생성
        for hour in range(0,24,1):
            for minute in range(0,60,m_interval):
                csv_filename = path+mac_name+"/" + mac_name + "_" + str(hour) + "_" + str(minute) + ".csv"
                csv_nameList.append(csv_filename)

                #mac키에 csv파일 이름 추가
                mac_csv_dc[mac_name].append(csv_filename)
        
        
    #시간별 csv 파일 생성
    for csvName in csv_nameList:
        with open(csvName,"w") as f:
            csv.writer(f)
        

    return mac_csv_dc