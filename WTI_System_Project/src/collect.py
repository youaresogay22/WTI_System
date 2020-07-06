import os
import filePath

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
    
def packet_filter(pcapng_name, csv_beacon_name=filePath.csv_beacon_path,
                     csv_probe_name=filePath.csv_probe_path, filter="all"):

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