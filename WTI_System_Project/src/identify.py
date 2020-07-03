"""
title : AP, Device Identify Module
author : YONG HWAN KIM (yh.kim951107@gmail.com)
date : 2020-07-03
detail : 
todo :
"""

import numpy as np
"""
param
ap_model : random_forest model
input : [clock skew, channel, rss, duration, ssid, mac address]
"""
def ap_identify(ap_model,ap_dic,becon_feature_input):
    target = becon_feature_input[4:6] # [ssid, mac address]
    x_input = np.array(becon_feature_input[0:4]).reshape(1,-1)

    #unknown ssid and mac address?
    if target not in ap_dic.values():
        print("unknown ap")
    else:
        answer = str(ap_model.predict(x_input)[0])
        print(ap_dic[answer])
    