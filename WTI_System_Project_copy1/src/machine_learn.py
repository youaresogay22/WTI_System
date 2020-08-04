"""
title : mechine learing moudle
author : YONG HWAN KIM (yh.kim951107@gmail.com)
date : 2020-07-15
detail : 
todo :
"""

import csv
import numpy as np
import prePro
import pandas as pd
import tensorflow.compat.v1 as tf
import pickle
import joblib
import filePath
import json

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn import metrics
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report

"""특징 데이터를 가져온다.
params
name : featuremodel.csv 파일 이름 경로

return
x_train : [[delta seq no, length], ... , [...]]
y_train : [[label], ... , [...]]
"""
def get_proReq_FeatureModel(name):
    x_train = []
    y_train = []
    with open(name,"r") as f:
        rdr = csv.reader(f)
        next(rdr,None) #header skip
        
        for row in rdr:
            x_train.append(list(map(float,row[:2])))  # [delta seq no, length]
            if row[-1]=="-1":                         # -1인 경우 매핑하지 않고 문자열 형식으로 저장한다.
                y_train.append([row[-1]])
            else:
                y_train.append(list(map(int,row[-1])))  # [label]
                
    return x_train, y_train

"""probe-request 학습데이터를 가져온다.
featuremodel.csv 파일들을 순회하며 학습데이터를 리스트에 저장한다.

parmas
fm_name_list : featuremodel.csv 파일 경로 리스트

return
feat_x_train : [[sequence number delta, length], ..., [...]]
feat_y_train : [label, ...]
"""
def get_proReq_train_data(fm_name_list):
    feat_x_train = []
    feat_y_train = []
    
    #featuremodel.csv 파일 리스트중에서 하나를 가져와 해당 featuremodel.csv 파일의 학습 데이터를 가공한다.
    for name in fm_name_list:
        x_train, y_train = get_proReq_FeatureModel(name)
        
        for data in x_train: #x_train 리스트를 feat_x_train 리스트에 누적한다.
            feat_x_train.append(data)
        for data in y_train: #y_train 리스트를 feat_y_train 리스트에 누적한다.
            feat_y_train.append(data[0]) #[0] => 0

    return feat_x_train, feat_y_train


"""학습 식별 모델을 생성한다.
학습 모델 타입은 랜덤 포레스트이다.

params
probe-request
data : [[sequence number delta, length], ..., [...]]
target : [label, ..., ]

becon-frame
data : [[clock skew, RSS, channel, duration], ... , [...]]
target : [[ssid,mac address], ..., [...]]
"""
def random_forest_model(data, target):
    rf = RandomForestClassifier(n_estimators=100,random_state=0)
    rf.fit(data,target)
    return rf