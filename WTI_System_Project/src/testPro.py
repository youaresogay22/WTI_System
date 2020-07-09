import file
import filePath
import machine_learn
import prePro

def proReq_testInputPorcess():
    mac_list = []           # wlan.sa list, list["fe:e6:1a:f1:d6:49", ... ,"f4:42:8f:56:be:89"]
    mac_pkt_dc = {}     # key:wlan.sa, value: probe-request(list)
    mac_csv_dc = {}     # key:wlan.sa, value: csv file names(list)
    csv_fm_list = []      # feature model file names for each wlan.sa(mac address)
    feat_x_train = []    # random forest model x_train
    feat_y_train = []    # random forest model y_train
    device_dic = {}         # key:label value: mac address

    prePro.preReq_Prepro()  # preprocessor wlan.seq(sequence number)

    mac_list = prePro.extract_macAddress(filePath.csv_probe_path)   # extract wlan.sa(mac address)
    
    file.make_macDirectory(filePath.probe_path,mac_list) # make each wlan.sa Directory
    
    mac_csv_dc = file.make_macCsvFile(filePath.probe_path,mac_list,10) # make csv file names list for each the wlan.sa

    mac_pkt_dc = prePro.extract_packetLine(filePath.csv_probeRe_path,mac_list) # extract probe-request for each the wlan.sa

    file.save_csvFile(filePath.probe_path,mac_pkt_dc,10) # save the probe-request data to the csv file for each the time

    # make feature csv file for each the wlan.sa
    for mac_name in mac_list:
        file.make_csvFeature(filePath.probe_path,mac_name,"seq")


    csv_fm_list, device_dic = file.init_seq_FeatureFile(mac_csv_dc) #a dd the feature data

    feat_x_train, _ = machine_learn.get_proReq_train_data(csv_fm_list) # return the training data about the probe-request

    return feat_x_train

def proReq_test(device_model,device_dic,x_test):
    #accuracy_score test
    #y_pred = rf.predict(x_test)
    #print("accuracy score :", metrics.accuracy_score(y_pred,y_test))
    #print(classification_report(y_pred,y_test))
    y_pred = device_model.predict(x_test)
    for x,y in zip(x_test,y_pred):
        if str(y) not in device_dic.keys():
            print("label : ",y)
            continue
        else:
            print("input :",x," label : ",y, " mac addr : ",device_dic[str(y)])
