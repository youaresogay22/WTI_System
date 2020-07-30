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
inputs : [[clock skew, channel, rss, duration, ssid, mac address]]
"""
def ap_identify(ap_model,ap_dic,inputs):
    for item in inputs:
        target = item[4:6]
        item = np.array(item[0:4]).reshape(1,-1) # [[clock skew, channel, rss, duration]]
        label = get_key(ap_dic,target) # 0, 1, ...

        #unknown ssid and mac address?
        if target not in ap_dic.values():
            print("ap_dic : ",ap_dic)
            print("Label : ",target)
            print("The Ap is unknown AP")
        else:
            pred = str(ap_model.predict(item)[0]) #output the label => [0], [1] , [2], [3], [4]...
            proba_list = ap_model.predict_proba(item)
            proba = np.max(proba_list)
            ident = ap_dic[pred]
            

            #classification result
            print("Classification result : AP ",pred,", Label : AP ",label)
            print("Proba : ", proba)
            if ident==target and proba>0.7:
                print("The Ap is authorized AP")
            else:
                print("The Ap is suspected to be a rogue AP")
        print("")

def get_key(ap_dic,value):
    for label, ident in ap_dic.items():
        if ident==value:
            return label
        
