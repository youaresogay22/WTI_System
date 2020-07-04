"""
title : AP, Device Identify Module
author : YONG HWAN KIM (yh.kim951107@gmail.com)
date : 2020-07-04
detail : 
todo :
"""

import numpy as np
"""
param
ap_model : random_forest model
input : [clock skew, channel, rss, duration, ssid, mac address]
"""
def ap_identify(ap_model,ap_dic,input):
    target = input[4:6] # [ssid, mac address]
    input = np.array(input[0:4]).reshape(1,-1)

    #unknown ssid and mac address?
    if target not in ap_dic.values():
        print("unknown ap")
    else:
        pred = str(ap_model.predict(input)[0]) #output the label => [0], [1] , [2], [3], [4]...
        proba_list = ap_model.predict_proba(input)
        proba = np.max(proba_list)
        ident = ap_dic[pred]
        
        if ident==target and proba>0.7:
            print("정상 AP")
        else:
            print("비인가 AP")
        
