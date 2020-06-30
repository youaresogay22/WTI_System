#!/usr/bin/env python
# coding: utf-8

# In[10]:

import tensorflow as tf
import csv
import pandas

# In[118]:

index1="1.csv"
index2="2.csv"
index3="3.csv"
index4="4.csv"
index5="5.csv"
index6="6.csv"
x_train=[]
y_train=[]

# In[119]:
#csv파일 읽고 데이터 리스트 만드는 부분

def read_csv(csvfile,x_train,y_train):
    colnames = ['sa','time_relative','seq','ssid','len']
    data = pandas.read_csv(csvfile,names=colnames)
    time=data.time_relative.tolist()
    seq=data.seq.tolist()
    
    for a in time:
        x_train.append(a)
    for b in seq:
        y_train.append(b)

# In[120]:

#전체 데이터 리스트 만들기

read_csv(index1,x_train,y_train)
read_csv(index2,x_train,y_train)
read_csv(index3,x_train,y_train)
read_csv(index4,x_train,y_train)
read_csv(index5,x_train,y_train)
read_csv(index6,x_train,y_train)

# In[124]:

#정규화를 위해 numpy배열로 변경하여 형태를 변경해줌

import numpy as np
x_train = np.array(x_train)
y_train = np.array(y_train)
x_train = x_train.reshape(-1, 1)
y_train = y_train.reshape(-1, 1)
# print(x_train.shape)
# print(y_train)

#기울기 표현을 위한 차트 그리는 부분

import matplotlib.pyplot as plt
plt.plot(x_train, y_train)
plt.show()

#실제 정규화부분(정규화를 위해 MinMaxScaler사용)

from sklearn.preprocessing import MinMaxScaler
x_scaler = MinMaxScaler()
y_scaler = MinMaxScaler()
x_train = x_scaler.fit_transform(x_train)

#한쪽의 차원에 맞게 정규화를 진행
y_train = x_scaler.transform(y_train)

# In[114]:

a=[1,2,3]
b=[4,5,6]
c=[7,8,9]
a.append(b)
print(a)

# In[137]:

#학습부분


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
    sess.run(train)
    if step%100 == 0:
        print(step,sess.run(cost), sess.run(W), x_scaler.inverse_transform(sess.run(b).reshape(-1,1)))

