import pandas as pd
import os
import time
import filePath
import tensorflow.compat.v1 as tf
import collect
import prePro
"""probe.csv를 참조하여 읽는다.

params
filename : .csv 파일 경로

return
data : DataFrame type
"""

csvname = "probe"
dev_name = []
def read_probe(filename):
    file_list = [filename]

    df_list = []

    for i in file_list:
        df = pd.read_csv(i, error_bad_lines=False)
        df = df.fillna("")
        df_list.append(df)
    
    data = df_list[0]

    return data

def separate_probe(dev_list,data,csvname="probe"):
    
    dummy = 0 

    for _sa in dev_list:
        dev_bssid = _sa.replace(":","_")
        #ospath = "./separated/" + csvname + "/" + dev_bssid
        ospath = filePath.packet_path + "/" + csvname + "/" + dev_bssid

        #mac별 디렉토리 생성
        if not os.path.isdir(ospath):
            os.makedirs(ospath)
        
        dummy = data[data["wlan.sa"]==_sa]
        indd = []
        timedif = []
        leng = []
        seqno = []
        
        for i in range(len(dummy)):
            #시퀀스 넘버의 사이클이 변경되는 지점(index)를 indd 리스트에 저장
            if i != 0 and dummy.iloc[i]["wlan.seq"] - dummy.iloc[i-1]["wlan.seq"] < 0:
                indd.append(i)
            
            #time을 0부터 시작하기 위해서 0번째 time을 빼주어 싱크로를 맞춘다.
            timedif.append(dummy.iloc[i]["frame.time_relative"] - dummy.iloc[0]["frame.time_relative"])

            #length 가공
            leng.append(dummy.iloc[i]["frame.len"] - len(dummy.iloc[i]["wlan.ssid"]))

        #시퀀스 넘버 전처리
        for i in range(len(indd)):
            if i == len(indd)-1:    #i가 마지막 인덱스인 경우
                dummy.iloc[indd[i]:]["wlan.seq"] = dummy.iloc[indd[i]:]["wlan.seq"] + 4096 *(i+1)
            else:
                dummy.iloc[indd[i]:indd[i+1]]["wlan.seq"] = dummy.iloc[indd[i]:indd[i+1]]["wlan.seq"] + 4096 * (i+1)

        #seqno list에 저장 및 0번째를 빼서 싱크로 맞추기
        for i in range(len(dummy)):
            seqno.append(dummy.iloc[i]["wlan.seq"] - dummy.iloc[0]["wlan.seq"])

        newdummy = pd.DataFrame({"sa" : dummy["wlan.sa"], "timedifference":timedif, "sequence no":seqno, "length" : leng})


        for i in range(144):
            ret = newdummy[newdummy["timedifference"] >= (i*600)][newdummy["timedifference"]<600 * (i+1)]
            if len(ret) < 14:
                continue
            filename = ospath + "/" + dev_bssid + "_" + str(i//6) + "_" + str((i%6)*10) + ".csv"
            ret.to_csv(filename, mode="w")

def process_delta(dev,csvname="probe"):
    global dev_name
    ap_name = []
    data_list = []
    data_size = []

    deltatime=[]
    deltaseq = []
    lost = []

    for i in range(144):
        dev_bssid = dev.replace(":","_")

        #ospath = "./separated/" + csvname + "/" + dev_bssid
        ospath = filePath.packet_path + "/" + csvname + "/" + dev_bssid
            
        filename = ospath + "/" + dev_bssid + "_" + str(i//6) + "_" + str((i%6)*10) + ".csv"

        try:
            df = pd.read_csv(filename)
            dev_name.append(filename)
            data_list.append(df)
            data_size.append(len(df))

            deltatime.append(df["timedifference"])
            deltaseq.append(df["sequence no"])
        except:
            lost.append([dev,i])
            continue
        
    
    dt = []
    ds = []
    for t,s in zip(deltatime, deltaseq):
        temp1 = []
        temp2 = []
        for i in range(len(t)):
            temp1.append(t[i]-t[0])
            temp2.append(s[i]-s[0])
        dt.append(temp1)
        ds.append(temp2)

    return dt, ds

def linear_regression(dt, ds):
    tf.disable_v2_behavior()

    W = tf.Variable(tf.random_normal([1]))
    b = tf.Variable(tf.random_normal([1]))

    X = tf.placeholder(tf.float32, shape=[None])
    Y = tf.placeholder(tf.float32, shape=[None])

    hypothesis = X * W + b

    cost = tf.reduce_mean(tf.square(hypothesis-Y))
    
    optimizer = tf.train.GradientDescentOptimizer(learning_rate = 0.000005)
    train = optimizer.minimize(cost)
    pattern = []
    pred = []
    costt = []
    sess = tf.Session()

    for i in range(len(dt)):
        sess.run(tf.global_variables_initializer())
        tempcost = []
        for step in range(501):
            _, cost_val, W_val, b_val = sess.run([train, cost, W, b],feed_dict={X:dt[i], Y:ds[i]})
            tempcost.append(W_val)

        print(step, W_val, cost_val)
        pattern.append(W_val)
        pred.append(W_val*ds[i] + b_val)
        costt.append(tempcost)

    return pattern
"""
data = read_probe(filePath.learn_csv_probe_path)

dev_list = ["f8:e6:1a:f1:d6:49"]

separate_probe(dev_list,data)



dt, ds = process_delta(dev_list)

linear_regression(dt,ds)
"""