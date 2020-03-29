import extract
import csv

#리스트 중복 제거
def remove_list_overlap(temp):
    return list(set(temp))



def make_macCsvFileNameList(mac_list):
    mac_csv_dc = {}

    #mac맥 csv파일리스트 맵의 키 설정
    for k in range(len(mac_list)):
        mac_csv_dc.update({mac_list[k]:[]})

    return mac_csv_dc


def init_macDictionary(mac_list):
        mac_dc = {}
    
        for idx in range(len(mac_list)):
            mac_dc[mac_list[idx]] = []

        return mac_dc