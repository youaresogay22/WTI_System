import filePath
import os
import pandas as pd

def separate_beacon(dev_list,data,csvname="beacon"):
    dummy = 0

    ts_relative = []
    #timedif = []
    for _sa in dev_list:
        dev_bssid = _sa.replace(":","_")
        ospath = filePath.packet_path +"/"+csvname + "/" + dev_bssid

        #mac별 디렉토리 생성
        if not os.path.isdir(ospath):
            os.makedirs(ospath)

        dummy = data[data["wlan.sa"]==_sa]
        
        for i in range(len(dummy)):
            ts_relative.append((dummy.iloc[i]["wlan.fixed.timestamp"]-dummy.iloc[0]["wlan.fixed.timestamp"])/1000000)
            #timedif.append(dummy.iloc[i]["frame.time_relative"] - dummy.iloc[0]["frame.time_relative"])
        
        newdummy = pd.DataFrame({"wlan.sa" : dummy["wlan.sa"],
                                "wlan.ssid" : dummy["wlan.ssid"],
                                "ts_relative" : ts_relative,
                                "frame.time_relative" : dummy["frame.time_relative"],
                                "wlan.ds.current_channel" : dummy["wlan.ds.current_channel"],
                                "wlan_radio.signal_dbm" : dummy["wlan_radio.signal_dbm"],
                                "wlan_radio.duration" : dummy["wlan_radio.duration"]
                                })
        
        for i in range(480):
            ret = newdummy[newdummy["frame.time_relative"]>=(i*180)][newdummy["frame.time_relative"]<180*(i+1)]
            if len(ret) <14:
                continue
            filename = ospath + "/" + dev_bssid + "_" + str(i//20) + "_" + str((i%20)*3) + ".csv"
            ret.to_csv(filename,mode="w")

def process_clockSkew(dev,csvname="beacon"):
    dev_name = []
    time_clock = []
    time_offset = []
    tc = []
    to = []
    lost = []
    for i in range(480):
        dev_bssid = dev.replace(":","_")

        ospath = filePath.packet_path + "/" + csvname + "/" + dev_bssid

        filename = ospath + "/" + dev_bssid + "_" + str(i//20) + "_" + str((i%20)*3) + ".csv"

        try:
            df = pd.read_csv(filename)
            dev_name.append(filename)

            for i in range(len(df)):
                time_clock_val = df.iloc[i]["frame.time_relative"]-df.iloc[0]["frame.time_relative"]
                time_offset_val = df.iloc[i]["ts_relative"] - df.iloc[0]["ts_relative"] - time_clock_val
                time_clock.append(time_clock_val)
                time_offset.append(time_offset_val)
            tc.append(time_clock)
            to.append(time_offset)
        except:
             lost.append([dev,i])
             continue
    
    

    return tc, to