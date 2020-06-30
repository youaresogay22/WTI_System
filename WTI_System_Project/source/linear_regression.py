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
#csv���� �а� ������ ����Ʈ ����� �κ�

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

#��ü ������ ����Ʈ �����

read_csv(index1,x_train,y_train)
read_csv(index2,x_train,y_train)
read_csv(index3,x_train,y_train)
read_csv(index4,x_train,y_train)
read_csv(index5,x_train,y_train)
read_csv(index6,x_train,y_train)

# In[124]:

#����ȭ�� ���� numpy�迭�� �����Ͽ� ���¸� ��������

import numpy as np
x_train = np.array(x_train)
y_train = np.array(y_train)
x_train = x_train.reshape(-1, 1)
y_train = y_train.reshape(-1, 1)
# print(x_train.shape)
# print(y_train)

#���� ǥ���� ���� ��Ʈ �׸��� �κ�

import matplotlib.pyplot as plt
plt.plot(x_train, y_train)
plt.show()

#���� ����ȭ�κ�(����ȭ�� ���� MinMaxScaler���)

from sklearn.preprocessing import MinMaxScaler
x_scaler = MinMaxScaler()
y_scaler = MinMaxScaler()
x_train = x_scaler.fit_transform(x_train)

#������ ������ �°� ����ȭ�� ����
y_train = x_scaler.transform(y_train)

# In[114]:

a=[1,2,3]
b=[4,5,6]
c=[7,8,9]
a.append(b)
print(a)

# In[137]:

#�н��κ�


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

