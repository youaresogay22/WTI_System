"""
title : Wireless terminal identification system
author : YONG HWAN KIM (yh.kim951107@gmail.com)
date : 2020-07-06
detail : 
todo :
"""

import csv
import os
import prePro
import machine_learn
import file
import filePath
import copy
import numpy as np
import identify
import collect

def proReq_process():
    mac_list = []           # wlan.sa list, list["fe:e6:1a:f1:d6:49", ... ,"f4:42:8f:56:be:89"]
    mac_pkt_dc = {}     # key:wlan.sa, value: probe-request(list)
    mac_csv_dc = {}     # key:wlan.sa, value: csv file names(list)
    csv_fm_list = []      # feature model file names for each wlan.sa(mac address)
    feat_x_train = []    # random forest model x_train
    feat_y_train = []    # random forest model y_train
   
    prePro.preReq_Prepro()  # preprocessor wlan.seq(sequence number)

    mac_list = prePro.extract_macAddress(filePath.csv_probe_path)   # extract wlan.sa(mac address)
    
    file.make_macDirectory(filePath.probe_path,mac_list) # make each wlan.sa Directory
    
    mac_csv_dc = file.make_macCsvFile(filePath.probe_path,mac_list,10) # make csv file names list for each the wlan.sa

    mac_pkt_dc = prePro.extract_packetLine(filePath.csv_probeRe_path,mac_list) # extract probe-request for each the wlan.sa

    file.save_csvFile(filePath.probe_path,mac_pkt_dc,10) # save the probe-request data to the csv file for each the time

    # make feature csv file for each the wlan.sa
    for mac_name in mac_list:
        file.make_csvFeature(filePath.probe_path,mac_name,"seq")

    csv_fm_list = file.init_seq_FeatureFile(mac_csv_dc) #a dd the feature data

    feat_x_train, feat_y_train = machine_learn.get_proReq_train_data(csv_fm_list) # return the training data about the probe-request

    machine_learn.random_forest_model(feat_x_train,feat_y_train) # make Device identify model

    
def beacon_process():
    bc_mac_list = []        # becon-frame wlan.sa list
    bc_mac_pkt_dc = {}  # key: wlan.sa , value: becon-frame(2-D list)
    bc_mac_csv_dc = {}  # key: wlan.sa, value: csv file names(list)
    bc_csv_fm_list = []   # becon-frame feature csv file names(list)
    ap_dic = {} # key : (ssid,MAC Address), value: label
    
    bc_mac_list = prePro.extract_macAddress(filePath.csv_beacon_path) # extract wlan.sa(mac address)
    
    file.make_macDirectory(filePath.beacon_path,bc_mac_list) # make Directory for each the wlan.sa

    """make csv file
    make becon-frame csv file
    return the csv file names list for each the wlan.sa
    """
    bc_mac_csv_dc = file.make_macCsvFile(filePath.beacon_path,bc_mac_list,3)

    """extract the becon-frame
    extract becon-frame for each the wlan.sa
    return the becon-frame dictionary for each wlan.sa
    """
    bc_mac_pkt_dc = prePro.extract_packetLine(filePath.csv_beacon_path,bc_mac_list)

    file.save_csvFile(filePath.beacon_path,bc_mac_pkt_dc,3) # save the becon-frame to csv file

    prePro.beacon_prepro(bc_mac_csv_dc) # preprocessor wlan.fixed.timestamp

    #make becon-frame feature csv file for each wlan.sa
    for mac_name in bc_mac_list:
        file.make_csvFeature(filePath.beacon_path,mac_name,frame="beacon")

    """save the feature data
    save the feature data for each the wlan.sa
    return the feature file csv names list
    """
    bc_csv_fm_list = file.init_beacon_FeatureFile(bc_mac_csv_dc)

    x_train, y_train, ap_dic = machine_learn.get_becon_train_data(bc_csv_fm_list) #get training data
    
    ap_model = machine_learn.random_forest_model(x_train,y_train) # make AP identify model
    
    machine_learn.save_model(ap_model,"ap_model.pkl") #save the model
    
    machine_learn.save_ap_label(ap_dic,"ap_label.json") #save the ap_dic

"""AP scan
Scan AP to create features of Becon frame

param
neti : network interface
1. 네트워크 인터페이스를 설정하여 becon frame 3분 탐색
2. becon frame 가공
3. 만들어진 레코드 반환

return
bf_feature : [clock skew, channel, rss, duration, ssid, mac address]
"""
def ap_scan(neti):
    os.system("sudo tshark -i {} -w ".format(neti)
                + filePath.pf_data_path
                + " -f \'wlan type mgt and (subtype beacon or subtype probe-req)\'"
                + " -a duration:{}".format(sec))

"""make directory
packet
 -probe
 -becon
pcapng
pcapng_csv
model
"""
def init_directory():
    """Make the Directory
    Make the pcapng_folder, csv Directory 
    """
    file.make_Directory(filePath.res_path)
    file.make_Directory(filePath.packet_path)   #packet
    file.make_Directory(filePath.probe_path)    #probe
    file.make_Directory(filePath.beacon_path)   #becon
    file.make_Directory(filePath.pf_path)       #pcapng
    file.make_Directory(filePath.csv_path)      #pcapng_csv
    file.make_Directory(filePath.model_path)    #model

def main():
    #init_directory()

    #collect.packet_collect("wlan1",5400) # collect the data

    collect.packet_filter(filePath.pf_data_path) #convert the pcapng file to csv file

    proReq_process() # preprocess the probe-request 
 
    beacon_process() #preprocess the becon frame and get AP Identify Model

    ap_model = machine_learn.load_model("ap_model.pkl")

    ap_dic = machine_learn.load_ap_label("ap_label.json")

    input = ["1.2490802157180465e-05","-21","9","2256","carlynne","88:36:6c:67:72:ec"]
    
    identify.ap_identify(ap_model,ap_dic,input)

if __name__=="__main__":
    main()



