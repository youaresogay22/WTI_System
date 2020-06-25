"""
title : Wireless terminal identification system
author : YONG HWAN KIM (yh.kim951107@gmail.com)
date : 2020-06-22
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

def packet_collect():

    """Set the NIC monitor mode
    Set the NIC(Network Interface Card) from managed mode to monitor mode
    """
    
    os.system("sudo ifconfig wlan1 down")
    os.system("sudo iwconfig wlan1 mode monitor")
    os.system("sudo ifconfig wlan1 up")
    
    """Make the Directory
    Make the pcapng_folder, csv Directory 
    """
    os.system("sudo mkdir "
                    +filePath.pf_path)
    os.system("sudo mkdir "
                    +filePath.csv_path)
    os.system("sudo chmod 777 "
                    +filePath.csv_path)
    
    """Capture the packet
    step1 Scan the becon frame or probe-request
    step2 select the frame field
    step3 save the becon frame and probe-request
    """
    
    os.system("sudo tshark -i wlan1 -w "
                    + filePath.pf_data_path
                    + " -f \'wlan type mgt and (subtype beacon or subtype probe-req)\'"
                    + " -a duration:3600")
    
    os.system("sudo tshark -r "
                    + filePath.pf_data_path
                    + " -Y \"wlan.fc.type_subtype==0x0004\""
                    + " -T fields -e wlan.sa -e frame.time_relative -e wlan.seq -e wlan.ssid -e frame.len -E separator=, -E quote=n -E header=y > "
                    + filePath.csv_probe_path)
    os.system("sudo tshark -r "
                    + filePath.pf_data_path
                    + " -Y \"wlan.fc.type_subtype==0x0008\" -T fields -e wlan.sa -e wlan.ssid -e wlan.fixed.timestamp -e frame.time_relative -e wlan.ds.current_channel -e wlan_radio.signal_dbm -e wlan_radio.duration -E separator=, -E quote=n -E header=y > "
                    + filePath.csv_beacon_path)

def proReq_process():
    mac_list = []           # wlan.sa list, list["fe:e6:1a:f1:d6:49", ... ,"f4:42:8f:56:be:89"]
    mac_pkt_dc = {}     # key:wlan.sa, value: probe-request(list)
    mac_csv_dc = {}     # key:wlan.sa, value: csv file names(list)
    csv_fm_list = []      # feature model file names for each wlan.sa(mac address)
    feat_x_train = []    # random forest model x_train
    feat_y_train = []    # random forest model y_train
   
    prePro.preReq_Prepro()  # preprocessor wlan.seq(sequence number)

    mac_list = prePro.extract_macAddress(filePath.csv_probe_path)   # extract wlan.sa(mac address)

    file.make_Directory(filePath.probe_path)    # make the probe Directory
    
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
    
    file.make_Directory(filePath.beacon_path) #make the becon Directory

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

    machine_learn.random_forest_model(x_train,y_train) # make AP identify model

def main():
    #packet_collect() # collect the data

    proReq_process() # preprocess the probe-request 
 
    beacon_process() #preprocess the becon frame

if __name__=="__main__":
    main()



