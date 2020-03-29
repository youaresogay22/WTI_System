"""
title : 맥 어드레스 추출
author : 김용환 (yh.kim951107@gmail.com)
date : 2020-03-29
detail : csv 파일을 읽어서 맥어드레스를 중복되지 않게 가공하여
리스트에 넣습니다.
     
"""
import csv
import os
import macPro
import seqPro
import timeTrans
import delSeqNum
import extract
import file

#main
def main():
    
    mac_list = []           #추출된 맥 리스트
    mac_dc = {}             #맥어드레스 딕셔너리, key:mac address value: 해당 맥 패킷데이터 리스트
    mac_csv_dc = {}       #mac별 csv파일 리스트

    #시퀀스번호 전처리
    seqPro.seq_Preprosessor()

    #맥 어드레스 추출 처리
    mac_list = extract.extract_macAddress()

    #probe폴더 생성
    file.make_probeDirectory()

    #mac폴더 생성
    file.make_macDirectory(mac_list)
    
    #mac별 csv 파일이름 리스트 생성
    mac_csv_dc = macPro.make_macCsvFileNameList(mac_list)
    
    #mac별 csv 파일 생성 및 mac별 csv파일 이름 리스트 설정
    file.make_csvFile(mac_list,mac_csv_dc)


    #step1 맥 어드레스 별 딕셔너리 초기화
    #mac_dc {key:mac_address value : 패킷리스트}
    mac_dc = macPro.init_macDictionary(mac_list)

    #step2 맥별 패킷 데이터 추출
    mac_dc = extract.extract_packetLine(mac_list,mac_dc)
    
    #step3 시간별 csv파일에 패킷데이터 저장
    file.save_csvFile(mac_list,mac_dc)
            
    #시간별 csv파일을 참조하여 시퀀스 넘버 증가량 추출
    num_increList = []
    time_list = []
    seqNum_list = []
    for key,value in mac_csv_dc.items():
        for idx in range(len(value)):
            csvFile = value[idx]           
            time_list = delSeqNum.make_timeRelative_list(csvFile)
            seqNum_list = delSeqNum.make_seqNumberList(csvFile)

            if not time_list or not seqNum_list:
                continue
            else:
                #시퀀스 넘버 기울기를 구하는 머신러닝 생성
                sess, hypothesis = delSeqNum.linear_regreesion(time_list,seqNum_list)
                
                
                
                
                
main()



