"""
title : mechine learing moudle
author : YONG HWAN KIM (yh.kim951107@gmail.com)
date : 2020-06-22
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

"""make training data
make the time data list for the sequence number delta

parmas
csvFile : file to open for the frame.time_relative data

return
time_list : frame.time_relative data list in csvFile
"""
def make_timeRelative_list(csvFile):    
    with open(csvFile,"r") as f:
        rdr = csv.reader(f)
        #time_list = prePro.extract_data_index(rdr,1) #extract frame.time_relative list
        time_list = list(map(float,prePro.extract_data_index(rdr,1)))
    return time_list


"""make training data
make the sequence number data list for the sequence number delta

params
csvFile : file to open for the wlan.seq data

return
seqNum_list : wlan.seq data list
"""
def make_seqNumberList(csvFile):
    seqNum_0 = 0    # 0th wlan.seq data
    seqNum_list = []
    
    with open(csvFile,"r") as f:
        rdr = csv.reader(f)
        temp_seqNum_list = prePro.extract_data_index(rdr,2) #extract wlan.seq data

        if temp_seqNum_list!=[]: # is not empty list
            seqNum_0 = float(temp_seqNum_list[0])
            for idx in range(len(temp_seqNum_list)):
                    seqNum_list.append((float(temp_seqNum_list[idx]) - seqNum_0))

    return seqNum_list

#선형 모델 기울기 반환
"""get click skew

becon-frame
x_train : wlan.fixed.timestamp list
y_train : i th frame.time_relative - 0th frame.time_relative) - i th wlan.fixed.timestamp, data list

return
becon-frame : clock skew
"""
def sklearn_linear_regression(x_train,y_train):
    
    X = np.array(x_train).astype(np.float64).reshape(-1,1)
    y = np.array(y_train).astype(np.float64)
    
    line_fitter = LinearRegression()
    line_fitter.fit(X,y)
    
    return line_fitter.coef_

"""get sequence number delta
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

    #optimizer = tf.train.GradientDescentOptimizer(learning_rate=0.001)
    optimizer = tf.train.MomentumOptimizer(learning_rate=0.0001,momentum=0.9)
    train = optimizer.minimize(cost)

    sess=tf.Session()
    sess.run(tf.global_variables_initializer())
    
    for step in range(50001):
        #_, cost_val, W_val, b_val = sess.run(train)
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
            y_train.append(label) #SSID, MAC Address
            target = row[4:6]
    
    return x_train ,y_train, target

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
    x_train, x_test, y_train, y_test = train_test_split(data,target,test_size=0.3,random_state=0)
    rf = RandomForestClassifier(n_estimators=100,random_state=0)
    rf.fit(x_train,y_train)

    
    #accuracy_score test
    y_pred = rf.predict(x_test)
    print("accuracy score :", metrics.accuracy_score(y_pred,y_test))
    print(classification_report(y_pred,y_test))

    return rf
    
"""save the model
param
model : machine learing training model
filename : saved model filename.pkl
"""
def save_model(model, filename):
    save_path = filePath.model_path + filename
    joblib.dump(model, save_path)

"""load the model
param
filename : model filename to load
"""
def load_model(filename):
    load_path = filePath.model_path + filename
    return joblib.load(load_path)

def save_label_dic(dic,filename):
    save_path = filePath.model_path + filename
    
    with open(save_path,"w") as json_file:
        json.dump(dic,json_file)

def load_label_dic(filename):
    load_path = filePath.model_path + filename

    with open(load_path,"r") as json_file:
        dic = json.load(json_file)
    return dic