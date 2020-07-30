import os
import filePath
import csv

def packet_collect(neti, sec,pcapng_name="data.pcapng"):

    """Set the NIC monitor mode
    Set the NIC(Network Interface Card) from managed mode to monitor mode
    """
    
    os.system("sudo ifconfig {} down".format(neti))
    os.system("sudo iwconfig {} mode monitor".format(neti))
    os.system("sudo ifconfig {} up".format(neti))
     
    """Capture the packet
    step1 Scan the becon frame or probe-request
    step2 select the frame field
    step3 save the becon frame and probe-request
    """
    os.system("sudo tshark -i {} -w ".format(neti)
                    + filePath.pf_data_path
                    + " -f \'wlan type mgt and (subtype beacon or subtype probe-req)\'"
                    + " -a duration:{}".format(sec))
    
    
def packet_filter(pcapng_name, csv_beacon_name=filePath.learn_csv_beacon_path,
                     csv_probe_name=filePath.learn_csv_probe_path, filter="all"):

    if filter=="all":
        os.system("sudo tshark -r "
                        + pcapng_name
                        + " -Y \"wlan.fc.type_subtype==0x0004\""
                        + " -T fields -e wlan.sa -e frame.time_relative -e wlan.seq -e wlan.ssid -e frame.len -E separator=, -E quote=n -E header=y > "
                        + csv_probe_name)
        os.system("sudo tshark -r "
                        + pcapng_name
                        + " -Y \"wlan.fc.type_subtype==0x0008\" -T fields -e wlan.sa -e wlan.ssid -e wlan.fixed.timestamp -e frame.time_relative -e wlan.ds.current_channel -e wlan_radio.signal_dbm -e wlan_radio.duration -E separator=, -E quote=n -E header=y > "
                        + csv_beacon_name)

    elif filter=="beacon":
        os.system("sudo tshark -r "
                        + pcapng_name
                        + " -Y \"wlan.fc.type_subtype==0x0008\" -T fields -e wlan.sa -e wlan.ssid -e wlan.fixed.timestamp -e frame.time_relative -e wlan.ds.current_channel -e wlan_radio.signal_dbm -e wlan_radio.duration -E separator=, -E quote=n -E header=y > "
                        + csv_beacon_name)

    elif filter=="probe":
        os.system("sudo tshark -r "
                        + pcapng_name
                        + " -Y \"wlan.fc.type_subtype==0x0004\""
                        + " -T fields -e wlan.sa -e frame.time_relative -e wlan.seq -e wlan.ssid -e frame.len -E separator=, -E quote=n -E header=y > "
                        + csv_probe_name)

def device_filter(filename,mode):
    dummy = []
    dev_list = []

    if mode=="probe":
        dev_list = [
            "f8:e6:1a:f1:d6:49", #A
            "84:2e:27:6b:53:df", #B
            "00:f4:6f:9e:c6:eb", #C
            "94:d7:71:fc:67:c9", #D
            "ac:36:13:5b:00:45", #E
            #"18:83:31:9b:75:ad",#F
        ]
        
        dummy.append(["wlan.sa",
                        "frame.time_relative",
                        "wlan.seq",
                        "wlan.ssid",
                        "frame.len"])

    elif mode=="beacon":
        dev_list = [
            "88:36:6c:67:72:ec",
            "08:5d:dd:65:39:0e"
        ]
        dummy.append(["wlan.sa",
                        "wlan.ssid",
                        "wlan.fixed.timestamp",
                        "frame.time_relative",
                        "wlan.ds.current_channel",
                        "wlan_radio.signal_dbm",
                        "wlan_radio.duration"])

    with open(filename,"r") as f:
        rdr = csv.reader(f)
        
        for line in rdr:
            if line[0] in dev_list:
                dummy.append(line)
    
    with open(filename,"w") as f:
        writer = csv.writer(f)
        writer.writerows(dummy)

def device_filter_testcase(filename,mode, train=True):
    dummy = []
    dev_list = []
    dev_dic = {
        "A": "f8:e6:1a:f1:d6:49",
        "B": "84:2e:27:6b:53:df",
        "C": "00:f4:6f:9e:c6:eb",
        "D": "94:d7:71:fc:67:c9",
        "E": "ac:36:13:5b:00:45",
        "F": "18:83:31:9b:75:ad",
    }
    ap_dev_dic = {
        "WIFI1": "88:36:6c:67:72:ec",
        "WIFI2": "08:5d:dd:65:39:0e",
    }
    if mode=="probe":
        if train==True: #train data filter
            testcase = int(input("input the train's probe testcase(1~6) : "))

            if testcase==1 or testcase==3 or testcase==4 or testcase==6:
                dev_list=[
                    dev_dic["A"],
                    dev_dic["B"],
                    dev_dic["C"],
                    dev_dic["D"],
                    dev_dic["E"]
                ]
            elif testcase==2 or testcase==5:
                dev_list=[
                    dev_dic["A"],
                    dev_dic["B"],
                    dev_dic["C"],
                    dev_dic["D"]
                ]
            else:
                pass
        else: #test data filter
            testcase = int(input("input the test's probe testcase(1~6) : "))
            if testcase==1 or testcase==4:
                dev_list=[
                    dev_dic["A"],
                    dev_dic["B"],
                    dev_dic["C"],
                    dev_dic["D"],
                    dev_dic["E"]
                ]
            elif testcase==2 or testcase==5:
                dev_list=[
                    dev_dic["A"],
                    dev_dic["B"],
                    dev_dic["C"],
                    dev_dic["E"],
                    dev_dic["F"]
                ]
            elif testcase==3 or testcase==6:
                dev_list=[
                    dev_dic["A"],
                    dev_dic["B"],
                    dev_dic["C"],
                    dev_dic["D"],
                    dev_dic["F"]
                ]
            else:
                pass

        dummy.append(["wlan.sa",
                        "frame.time_relative",
                        "wlan.seq",
                        "wlan.ssid",
                        "frame.len"])

    elif mode=="beacon":
        if train==True: #train data filter
            dev_list = [ap_dev_dic["WIFI1"]]
        else: #test data filter
            testcase = int(input("input the test's beacon testcase(0~6) : "))
            if testcase==0:
                dev_list = [ap_dev_dic["WIFI1"],
                            ap_dev_dic["WIFI2"]]
            elif testcase==1 or testcase==2 or testcase==3:
                dev_list = [ap_dev_dic["WIFI1"]]
            elif testcase==4 or testcase==5 or testcase==6:
                dev_list = [ap_dev_dic["WIFI2"]]            
            else:
                pass

        dummy.append(["wlan.sa",
                        "wlan.ssid",
                        "wlan.fixed.timestamp",
                        "frame.time_relative",
                        "wlan.ds.current_channel",
                        "wlan_radio.signal_dbm",
                        "wlan_radio.duration"])

    with open(filename,"r") as f:
        rdr = csv.reader(f)
        
        for line in rdr:
            if line[0] in dev_list:
                dummy.append(line)
    
    with open(filename,"w") as f:
        writer = csv.writer(f)
        writer.writerows(dummy)
