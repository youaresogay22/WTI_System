"""
title : file path variables
author : YONG HWAN KIM (yh.kim951107@gmail.com)
date : 2020-06-22
detail : 
todo :
"""

import os 

path = os.getcwd()
probe_path = path + "/probe/"
beacon_path = path + "/beacon/"
pf_path = path + "/pcapng_folder"
pf_data_path = pf_path + "/data.pcapng"
csv_path = path + "/csv"
csv_probe_path = csv_path + "/probe.csv"
csv_probeRe_path = csv_path + "/probe_re.csv"
csv_beacon_path = csv_path + "/beacon.csv"
