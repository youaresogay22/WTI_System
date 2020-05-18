"""
title : 무선단말 패킷 데이터 추출 및 가공 시스템
author : 김용환 (yh.kim951107@gmail.com)
date : 2020-05-17
detail : 
todo : 
beacon frame 의 mac별 timestamp 전처리 필요
sudo dumpcap -i wlan1 -w /home/user/Desktop/git/WTI_System_Project/source/pcapng_folder/data.pcapng 'wlan_type mgt and (wlan_subtype beacon or wlan_subtype probe-req)' -a duration:86400
"""
import csv
import os
import prePro
import machine_learn
import file
import filePath
import copy

def packet_collect():

    #NIC 모니터 모드 설정
    os.system("sudo ifconfig wlan1 down")
    os.system("sudo iwconfig wlan1 mode monitor")
    os.system("sudo ifconfig wlan1 up")

    #디렉터리 생성

    os.system("sudo mkdir " +filePath.pf_path)
    os.system("sudo mkdir " +filePath.csv_path)
    os.system("sudo chmod 777 " + filePath.csv_path)

    #패킷 캡처 명령어
    os.system("sudo tshark -i wlan1 -w " + filePath.pf_data_path + " -f \'wlan type mgt and (subtype beacon or subtype probe-req)\' -a duration:86400")
    #os.system("sudo dumpcap -i wlan1 -w /home/user/Desktop/git/WTI_System_Project/source/pcapng_folder/data.pcapng 'wlan_type mgt and (wlan_subtype beacon or wlan_subtype probe-req)' -a duration:86400")
    os.system("sudo tshark -r " + 
                        filePath.pf_data_path +
                         " -Y \"wlan.fc.type_subtype==0x0004\" -T fields -e wlan.sa -e frame.time_relative -e wlan.seq -e wlan.ssid -e frame.len -E separator=, -E quote=n -E header=y > " + filePath.csv_probe_path)
    os.system("sudo tshark -r "+filePath.pf_data_path + " -Y \"wlan.fc.type_subtype==0x0008\" -T fields -e wlan.sa -e wlan.ssid -e wlan.fixed.timestamp -e frame.time_relative -e wlan.ds.current_channel -e wlan_radio.signal_dbm -e wlan_radio.duration -E separator=, -E quote=n -E header=y > "+filePath.csv_beacon_path)

def proReq_process():
    mac_list = []           #추출된 맥 리스트
    mac_pkt_dc = {}             #맥어드레스 딕셔너리, key:mac address value: 해당 맥 패킷데이터 리스트
    mac_csv_dc = {}       #mac별 csv파일 리스트

   #시퀀스번호 및 길이 전처리
    prePro.preReq_Prepro()

    #맥 어드레스 추출
    mac_list = prePro.extract_macAddress(filePath.csv_probe_path)
    
    #probe 폴더 생성
    file.make_Directory(filePath.probe_path)

    #mac별 폴더 생성
    file.make_macDirectory(filePath.probe_path,mac_list)
    
    #mac별 csv 파일이름 리스트 생성
    mac_csv_dc = file.make_macCsvFile(filePath.probe_path,mac_list,10)

    #맥별 패킷 데이터 추출
    mac_pkt_dc = prePro.extract_packetLine(filePath.csv_probeRe_path,mac_list)

    #시간별 csv파일에 패킷데이터 저장
    file.save_csvFile(filePath.probe_path,mac_pkt_dc,10)

    #mac별 Feature 추출 모델 파일 생성
    for mac_name in mac_list:
        file.make_csvFeature(filePath.probe_path,mac_name,"seq")

    #디바이스별 Feature 추출 모델 데이터 작성
    file.init_seq_FeatureFile(mac_csv_dc)


def beacon_process():
    bc_mac_list = []
    bc_mac_pkt_dc = {}
    bc_mac_csv_dc = {}

    #beacon 폴더 생성
    file.make_Directory(filePath.beacon_path)

    #beacon.csv의 mac 리스트 생성
    bc_mac_list = prePro.extract_macAddress(filePath.csv_beacon_path)
    
    #mac별  폴더 생성
    file.make_macDirectory(filePath.beacon_path,bc_mac_list)

    #mac별 시간으로 구분한 csv파일 생성
    bc_mac_csv_dc = file.make_macCsvFile(filePath.beacon_path,bc_mac_list,3)

    #맥별 패킷 데이터 추출
    bc_mac_pkt_dc = prePro.extract_packetLine(filePath.csv_beacon_path,bc_mac_list)

    #비콘 시간 수신 데이터 전처리
    bc_mac_pkt_dc =  prePro.beacon_prepro(bc_mac_pkt_dc)
        
    #맥별 패킷 데이터 csv에 저장
    file.save_csvFile(filePath.beacon_path,bc_mac_pkt_dc,3)

    #mac별 Feature 추출 모델 파일 생성
    for mac_name in bc_mac_list:
        file.make_csvFeature(filePath.beacon_path,mac_name,frame="beacon")

    file.init_beacon_FeatureFile(bc_mac_csv_dc)

#main
def main():
    
    #패킷 수집
    #packet_collect()

    #probe-request data 가공
    proReq_process()
 
    #beacon frame 가공
    beacon_process()

 
if __name__=="__main__":
    main()



