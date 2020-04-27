"""
title : 무선단말 패킷 데이터 추출 및 가공 시스템
author : 김용환 (yh.kim951107@gmail.com)
date : 2020-04-21
detail : 
todo : 
linear regression 관련해서 최적화 필요

"""
import csv
import os
import macPro
import seqPro
import timeTrans
import delSeqNum
import extract
import file
import filePath
def packet_collect():

    #NIC 모니터 모드 설정
    os.system("sudo ifconfig wlan0 down")
    os.system("sudo iwconfig wlan0 mode monitor")
    os.system("sudo ifconfig wlan0 up")

    #디렉터리 생성

    os.system("sudo mkdir " +filePath.pf_path)
    os.system("sudo mkdir " +filePath.csv_path)
    os.system("sudo chmod 777 " + filePath.csv_path)

    #패킷 캡처 명령어
    os.system("sudo tshark -i wlan0 -w " + filePath.pf_data_path + " -f \'wlan type mgt and (subtype probe-req)\' -a duration:86400")
    os.system("sudo tshark -r " + 
                        filePath.pf_data_path +
                         " -Y \"wlan.fc.type_subtype==0x0004\" -T fields -e wlan.sa -e frame.time_relative -e wlan.seq -e wlan.ssid -e frame.len -E separator=, -E quote=n -E header=y > " + filePath.csv_probe_path)

#main
def main():
    
    mac_list = []           #추출된 맥 리스트
    mac_dc = {}             #맥어드레스 딕셔너리, key:mac address value: 해당 맥 패킷데이터 리스트
    mac_csv_dc = {}       #mac별 csv파일 리스트

    #packet_collect()

    #시퀀스번호 전처리
    seqPro.seq_Preprosessor()

    #맥 어드레스 추출
    mac_list = extract.extract_macAddress()

    #probe폴더 생성
    file.make_probeDirectory()

    #mac별 폴더 생성
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

    #mac별 Feature 추출 모델 파일 생성
    for idx in range(len(mac_list)):
        file.make_csvFeature(mac_list[idx])

    #디바이스별 Feature 추출 모델 데이터 작성
    file.init_FeatureFile(mac_csv_dc)

if __name__=="__main__":
    main()



