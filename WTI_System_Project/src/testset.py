import file
import filePath
import machine_learn
import prePro

def proReq_createTestset():
    mac_list = []           # wlan.sa list, list["fe:e6:1a:f1:d6:49", ... ,"f4:42:8f:56:be:89"]
    mac_pkt_dc = {}     # key:wlan.sa, value: probe-request(list)
    mac_csv_dc = {}     # key:wlan.sa, value: csv file names(list)
    csv_fm_list = []      # feature model file names for each wlan.sa(mac address)
    feat_x_train = []    # random forest model x_train
    feat_y_train = []    # random forest model y_train
    device_dic = {}         # key:label value: mac address

    prePro.preReq_Prepro(filePath.test_csv_probe_path,filePath.test_csv_probeRe_path)  # preprocessor wlan.seq(sequence number)

    mac_list = prePro.extract_macAddress(filePath.test_csv_probe_path)   # extract wlan.sa(mac address)
    
    file.make_macDirectory(filePath.probe_test_path,mac_list) # make each wlan.sa Directory
    
    mac_csv_dc = file.make_macCsvFile(filePath.probe_test_path,mac_list,10) # make csv file names list for each the wlan.sa

    mac_pkt_dc = prePro.extract_packetLine(filePath.test_csv_probeRe_path,mac_list) # extract probe-request for each the wlan.sa

    file.save_csvFile(filePath.probe_test_path,mac_pkt_dc,10) # save the probe-request data to the csv file for each the time

    # make feature csv file for each the wlan.sa
    for mac_name in mac_list:
        file.make_csvFeature(filePath.probe_test_path,mac_name,"seq")


    csv_fm_list, device_dic = file.init_seq_FeatureFile(mac_csv_dc,filePath.probe_test_path) #a dd the feature data

    feat_x_train, _ = machine_learn.get_proReq_train_data(csv_fm_list) # return the training data about the probe-request

    return feat_x_train

def packet_test(model,dic,x_input):
    #accuracy_score test
    #y_pred = rf.predict(x_test)
    #print("accuracy score :", metrics.accuracy_score(y_pred,y_test))
    #print(classification_report(y_pred,y_test))
    y_pred = model.predict(x_input)
    for x,y in zip(x_input,y_pred):
        if str(y) not in dic.keys():
            continue
        else:
            print("input :",x," label : ",y, " mac addr : ",dic[str(y)])


def beacon_createTestset():
    bc_mac_list = []        # becon-frame wlan.sa list
    bc_mac_pkt_dc = {}  # key: wlan.sa , value: becon-frame(2-D list)
    bc_mac_csv_dc = {}  # key: wlan.sa, value: csv file names(list)
    bc_csv_fm_list = []   # becon-frame feature csv file names(list)
    ap_dic = {} # key : (ssid,MAC Address), value: label
    
    bc_mac_list = prePro.extract_macAddress(filePath.test_csv_beacon_path) # extract wlan.sa(mac address)
    
    file.make_macDirectory(filePath.beacon_test_path,bc_mac_list) # make Directory for each the wlan.sa

    """make csv file
    make becon-frame csv file
    return the csv file names list for each the wlan.sa
    """
    bc_mac_csv_dc = file.make_macCsvFile(filePath.beacon_test_path,bc_mac_list,3)

    """extract the becon-frame
    extract becon-frame for each the wlan.sa
    return the becon-frame dictionary for each wlan.sa
    """
    bc_mac_pkt_dc = prePro.extract_packetLine(filePath.test_csv_beacon_path,bc_mac_list)

    file.save_csvFile(filePath.beacon_test_path,bc_mac_pkt_dc,3) # save the becon-frame to csv file

    prePro.beacon_prepro(bc_mac_csv_dc) # preprocessor wlan.fixed.timestamp

    #make becon-frame feature csv file for each wlan.sa
    for mac_name in bc_mac_list:
        file.make_csvFeature(filePath.beacon_test_path,mac_name,frame="beacon")

    """save the feature data
    save the feature data for each the wlan.sa
    return the feature file csv names list
    """
    bc_csv_fm_list = file.init_beacon_FeatureFile(bc_mac_csv_dc,becon_path=filePath.beacon_test_path)

    x_train, _ , _ = machine_learn.get_becon_train_data(bc_csv_fm_list) #get training data

    return x_train