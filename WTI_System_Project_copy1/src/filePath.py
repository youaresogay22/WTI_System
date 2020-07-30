"""
title : file path variables
author : YONG HWAN KIM (yh.kim951107@gmail.com)
date : 2020-07-13
detail : 
todo :
"""

import os 

path = os.getcwd()

res_path = path + "/../res/"

packet_path = res_path + "/packet/"
probe_path = packet_path + "/probe/"
probe_test_path = packet_path + "/probe_test/"
beacon_path = packet_path + "/beacon/"
beacon_test_path = packet_path + "/beacon_test/"

pf_path = res_path + "/pcapng"
pf_data_path = pf_path + "/data.pcapng"

csv_path = res_path + "/pcapng_csv"
pcapng_csv_learn = csv_path + "/learn/"
pcapng_csv_test = csv_path + "/test/"
learn_csv_probe_path = pcapng_csv_learn + "/probe.csv"
learn_csv_probe2_path = pcapng_csv_learn + "/probe2.csv"
learn_csv_probeRe_path = pcapng_csv_learn + "/probe_re.csv"
learn_csv_beacon_path = pcapng_csv_learn + "/beacon.csv"
test_csv_probe_path = pcapng_csv_test + "/probe.csv"
test_csv_probeRe_path = pcapng_csv_test + "/probe_re.csv"
test_csv_beacon_path = pcapng_csv_test + "/beacon.csv"

model_path = res_path + "/model/"

scan_path = res_path + "/scan/"
scan_probe_path = scan_path + "/probe/"
scan_beacon_path = scan_path + "/beacon/"
scan_beacon_data_path = scan_beacon_path + "/data.pcapng"
scan_beacon_csv_path = scan_beacon_path + "/becon.csv"

packet_test = res_path + "/packet_test/"
packet_test_probe_path = packet_test + "/probe/"
packet_test_beacon_path = packet_test + "/beacon/"
packet_test_probe_csv_path = packet_test_probe_path + "/probe_test.csv"
packet_test_beacon_csv_path = packet_test_beacon_path + "/beacon_test.csv"

