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

"""x_train 추출
timedifference를 구한다.
각각의 파일에서 time_relative를 참조하고 해당 파일의 0번째 time_relative를 빼서
timedifference를 구한다.

parmas
csvFile : 참조하고자 하는 파일

return
delta_time : t_i - t_0 식을 적용한 리스트
"""
def make_timeRelative_list(csvFile):
    delta_time = []    
    with open(csvFile,"r") as f:
        rdr = csv.reader(f)
        time_list = list(map(float,prePro.extract_data_index(rdr,1)))

        if time_list != []:
            time_0 = float(time_list[0])
            for idx in range(len(time_list)):
                delta_time.append((float(time_list[idx])-time_0))
    return delta_time


"""y_train 추출
각각의 파일에서 wlan.seq를 참조하여 해당 파일의 0번째 wlan.seq를 빼서
sequence number difference 리스트를 새성하여 반환한다.

params
csvFile : 참조하고자 하는 파일

return
delta_seqNum_list : s_i - s_0을 계산한 시퀀스넘버 차이 리스트 
"""
def make_seqNumberList(csvFile):
    seqNum_0 = 0    # 0번째 시퀀스넘버 데이터
    delta_seqNum_list = []
    
    with open(csvFile,"r") as f:
        rdr = csv.reader(f)
        temp_seqNum_list = prePro.extract_data_index(rdr,2) # wlan.seq 추출

        if temp_seqNum_list!=[]:
            seqNum_0 = float(temp_seqNum_list[0])
            for idx in range(len(temp_seqNum_list)):
                    #seuqnce number difference를 계산한다.
                    delta_seqNum_list.append((float(temp_seqNum_list[idx]) - seqNum_0))

    return del_ta_seqNum_list


"""clock skew 기울기 계산

becon-frame
x_train : wlan.fixed.timestamp list
y_train : i th frame.time_relative - 0th frame.time_relative) - i th wlan.fixed.timestamp, data list

return
line_fitter.coef_ : clock skew
"""
def sklearn_linear_regression(x_train,y_train):
    
    X = np.array(x_train).astype(np.float64).reshape(-1,1)
    y = np.array(y_train).astype(np.float64)
    
    line_fitter = LinearRegression()
    line_fitter.fit(X,y)
    
    return line_fitter.coef_

"""시퀀스 넘버 증가율(delta seq no) 계산
params
probe-request
x_train : frame.time_relative
y_train : wlan.seq

return
probe-request : sequence number delta
"""
def tensor_linear_regression(x_train,y_train):
    tf.disable_v2_behavior()
    tf.set_random_seed(777)
    
    x_train = np.array(x_train)
    y_train = np.array(y_train)
    x_train = x_train.reshape(-1, 1)
    y_train = y_train.reshape(-1, 1)

    x_scaler = MinMaxScaler()
    y_scaler = MinMaxScaler()
    x_train = x_scaler.fit_transform(x_train)

    y_train = x_scaler.transform(y_train)

    W=tf.Variable(tf.random_normal([1]), name="weight")
    b=tf.Variable(tf.random_normal([1]), name="bias")

    hypothesis = x_train*W+b
    cost = tf.reduce_mean(tf.square(hypothesis-y_train))

    optimizer = tf.train.GradientDescentOptimizer(learning_rate=0.000005)
    #optimizer = tf.train.MomentumOptimizer(learning_rate=0.001,momentum=0.9)
    train = optimizer.minimize(cost)

    sess=tf.Session()
    sess.run(tf.global_variables_initializer())
    
    for step in range(501):
        sess.run(train)
        if step%100 == 0:
            print(step,sess.run(cost), sess.run(W), x_scaler.inverse_transform(sess.run(b).reshape(-1,1)))
    
    return sess.run(W)


##############################################################################
"""get feature data
open the feature file and then input to x_train, y_train
"""
def get_proReq_FeatureModel(name):
    x_train = []
    y_train = []
    with open(name,"r") as f:
        rdr = csv.reader(f)
        next(rdr,None) #header skip
        
        for row in rdr:
            x_train.append(list(map(float,row[:2])))  # convert all str list to integer list
            y_train.append(list(map(int,row[-1])))  # conver all str list to integer list

    return x_train, y_train

def get_proReq_AVG_FeatureModel(name):
    x_train = []
    y_train = None
    with open(name,"r") as f:
        rdr = csv.reader(f)
        next(rdr,None) #header skip
        length = 0
        delta_seq_list = []
        sum = 0
        for row in rdr:
            delta_seq_list.append(float(row[0]))
            length = int(row[1])
            y_train = int(row[2])
        
        for i in range(len(delta_seq_list)):
            sum += delta_seq_list[i]

        delta_seq_avg = sum / len(delta_seq_list)
        x_train.append([delta_seq_avg,length])
    return x_train, y_train
"""get training data
get probe-request training data to use the random forest

parmas
csv_fm_list : feature csv file names

return
feat_x_train : sequence number delta, length
feat_y_train : label
"""
def get_proReq_train_data(csv_fm_list):
    feat_x_train = []
    feat_y_train = []
    
    #get feature data and then save the training data
    for name in csv_fm_list:
        x_train, y_train = get_proReq_FeatureModel(name)
        
        for data in x_train: #reduce the x_train data
            feat_x_train.append(data)
        for data in y_train: #reduce the y_train data
            feat_y_train.append(data[0]) #[0] => 0

    return feat_x_train, feat_y_train

def get_proReq_train_data_AVG(csv_fm_list):
    feat_x_train = []
    feat_y_train = []
    
    #get feature data and then save the training data
    for name in csv_fm_list:
        x_train, y_train = get_proReq_AVG_FeatureModel(name)
        
        for data in x_train: #reduce the x_train data
            feat_x_train.append(data)
        feat_y_train.append(y_train)

    return feat_x_train, feat_y_train
"""get feature data
get x_train, y_train data to use the random forest model
x_train : ClockSkew, RSS, channel, duration
y_train : label

params
name : feature csv file name

key : (ssid,mac address) value : label
"""
def get_becon_FeatureModel(name,label):
    x_train = []
    y_train = []
    target = ()
    with open(name,"r") as f:
        rdr = csv.reader(f)
        next(rdr,None) #header skip

        for row in rdr: #extract and process the x_train
            x_train.append(row[0:4]) #ClockSkew, RSS, channel, duration
            y_train.append(label) 
            target = row[4:6] #SSID, MAC Address
    
    return x_train ,y_train, target

def get_becon_test_FeatureModel(name,ap_label):
    x_train = []
    y_train = []
    target = ()
    with open(name,"r") as f:
        rdr = csv.reader(f)
        next(rdr,None) #header skip

        for row in rdr: #extract and process the x_train
            x_train.append(row[0:4]) #ClockSkew, RSS, channel, duration 
            target = row[4:6] #SSID, MAC Address

            for label, value in ap_label.items():
                if target==value:
                    y_train.append(label)
            
    return x_train ,y_train


"""get becon-frame training data

params
csv_fm_list : feature csv file names

return
feat_x_train : clock skew, RSS, channel, duration,
feat_y_train : ssid,mac address
ap_dic : key: label, value:(SSID,MAC Address)
"""
def get_becon_train_data(csv_fm_list):
    feat_x_train = []
    feat_y_train = []
    ap_dic = {}
    label = 0
    
    for name in csv_fm_list:
        x_train, y_train, target = get_becon_FeatureModel(name,label)
        ap_dic.update({label : target})
        label += 1
        for data in x_train:
            feat_x_train.append(data)
        for data in y_train:
            feat_y_train.append(data)
    
    
    return feat_x_train, feat_y_train, ap_dic
    
def get_becon_test_train_data(csv_fm_list,ap_label):
    feat_x_train = []
    feat_y_train = []

    for name in csv_fm_list:
        x_train,y_train = get_becon_test_FeatureModel(name,ap_label)
        
        for data in x_train:
            feat_x_train.append(data)
        for data in y_train:
            feat_y_train.append(data)
    
    
    return feat_x_train, feat_y_train

"""create device identify model
model type is random forest model

params
probe-request
data : sequence number delta, length
target : label

becon-frame
data : clock skew, RSS, channel, duration,
target : ssid,mac address
"""
def random_forest_model(data, target):
    rf = RandomForestClassifier(n_estimators=100,random_state=0)
    rf.fit(data,target)
    return rf
    
"""save the model
param
model : machine learing training model
filename : saved model filename.pkl
"""
def save_model(model, filename):
    save_path = filePath.model_path + filename
    joblib.dump(model, save_path)

def save_label_dic(dic,filename):
    save_path = filePath.model_path + filename
    
    with open(save_path,"w") as json_file:
        json.dump(dic,json_file)

"""load the model
param
filename : model filename to load
"""
def load_model(filename):
    load_path = filePath.model_path + filename
    return joblib.load(load_path)

def load_label_dic(filename):
    load_path = filePath.model_path + filename

    with open(load_path,"r") as json_file:
        dic = json.load(json_file)
    return dic