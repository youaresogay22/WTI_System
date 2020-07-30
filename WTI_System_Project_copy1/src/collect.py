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

def device_filter(filename,savename,mode):
    dummy = []
    dev_list = []

    if mode=="probe":
        """
        dev_list = [
            "f8:e6:1a:f1:d6:49",
            "84:2e:27:6b:53:df",
            "00:f4:6f:9e:c6:eb",
            "94:d7:71:fc:67:c9",
            "ac:36:13:5b:00:45",
            #"18:83:31:9b:75:ad",
        ]
        """
        """
        dev_list = [
            "f8:e6:1a:f1:d6:49"
        ]
        """

        dev_list = [
            "2c:33:7a:2b:79:3a",
            "34:08:04:9b:31:79",
            "80:2b:f9:f1:5e:e9",
            "88:36:6c:f9:ca:76",
            "04:cf:8c:89:18:47",
            "ac:fd:ce:b0:da:79",
            "58:65:e6:70:38:be",
            "1c:f2:9a:69:bf:0b",
            "a8:2b:b9:b9:de:42",
            "0c:1c:20:0c:38:84",
            "60:36:dd:5e:d0:9e",
            "7c:38:ad:28:05:48",
            "ac:d1:b8:cb:6b:cb"
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
            try:
                if line[1] in dev_list:
                    dummy.append([line[1],line[2],line[4],line[0],line[6]])
            except:
                continue
    
    with open(savename,"w") as f:
        writer = csv.writer(f)
        writer.writerows(dummy)
