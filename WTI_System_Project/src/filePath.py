"""
title : file path variables
author : YONG HWAN KIM (yh.kim951107@gmail.com)
date : 2020-06-22
detail : 
todo :
"""

import os 

path = os.getcwd()

res_path = path + "/../res/"

packet_path = res_path + "/packet/"
probe_path = packet_path + "/probe/"
beacon_path = packet_path + "/beacon/"

pf_path = res_path + "/pcapng"
pf_data_path = pf_path + "/data.pcapng"

csv_path = res_path + "/pcapng_csv"
csv_probe_path = csv_path + "/probe.csv"
csv_probeRe_path = csv_path + "/probe_re.csv"
csv_beacon_path = csv_path + "/beacon.csv"

model_path = res_path + "/model/"

scan_path = res_path + "/scan/"
scan_probe_path = scan_path + "/probe/"
scan_beacon_path = scan_path + "/beacon/"
scan_beacon_data_path = scan_beacon_path + "/data.pcapng"
scan_beacon_csv_path = scan_beacon_path + "/becon.csv"