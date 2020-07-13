import pandas as pd
import os
import filePath
import copy
import tensorflow.compat.v1 as tf


def prepro_seq():
    file_list = [filePath.csv_probe_path]
    df_list = []
    for i in file_list:
        df = pd.read_csv(i,error_bad_lines=False)
        df = df.fillna("")
        df_list.append(df)
    
    data = df_list[0]
    ##########################

    dev_list = [
        "84:2e:27:6b:53:df",
        "3c:a0:67:85:86:1b",
        "94:d7:71:fc:67:c9",
        "f8:e6:1a:f1:d6:49",
        "00:f4:6f:9e:c6:eb"
    ]
    csvname = "1118 to 1122_total_day"
    dummy = 0
    for _sa in dev_list:
        dev_bssid = _sa.replace(":","_")
        ospath = "./separated/"+csvname+"/"+dev_bssid

        #each dev_list item make the directory
        if not os.path.isdir(ospath):
            os.makedirs(ospath)

        #맥별 데이터 구분
        dummy = data[data["wlan.sa"] == _sa]
        print(_sa)
        indd = []
        timedif = []
        leng = []
        seqno = []
        for i in range(len(dummy)):
            #print(i, dummy.iloc[i]["wlan.seq"], dummy.iloc[0]["wlan.seq"])
            if i != 0 and dummy.iloc[i]["wlan.seq"] - dummy.iloc[i-1]["wlan.seq"] < 0:
                indd.append(i)

            timedif.append(dummy.iloc[i]["frame.time_relative"] - dummy.iloc[0]["frame.time_relative"])
            leng.append(dummy.iloc[i]["frame.len"] - len(dummy.iloc[i]["wlan.ssid"]))


        #print(dummy.iloc[indd]["wlan.seq"])
        #print(indd)
        for i in range(len(indd)):
            if i == len(indd) - 1:
                dummy.iloc[indd[i]:]["wlan.seq"] = dummy.iloc[indd[i]:]["wlan.seq"] + 4096 * (i+1)
            else:
                #print(i)
                dummy.iloc[indd[i]:indd[i+1]]["wlan.seq"] = dummy.iloc[indd[i]:indd[i+1]]["wlan.seq"] + 4096 * (i+1)
                #print(i,dummy.iloc[i]["wlan.seq"])
        for i in range(len(dummy)):
            seqno.append(dummy.iloc[i]["wlan.seq"] - dummy.iloc[0]["wlan.seq"])     

        #print(dummy["wlan.sa"], len(timedif) , len(seqno) , len(leng))
        newdummy = pd.DataFrame({'sa' : dummy["wlan.sa"], 'timedifference':timedif, 'sequence no':seqno, 'length':leng})

        #newdummy.to_csv(filePath.csv_probeRe_path,mode="a",header=False,index=False)
        
        for i in range(5):
            ret = newdummy[newdummy['timedifference'] >= (i*86400) ][newdummy['timedifference'] < 86400*(i+1)]
            filename = ospath + "/"+dev_bssid +"_" + str(i)+ ".csv"
            ret.to_csv(filename, mode = "w")
            print(filename)
         
        #filename = ospath+ ".csv"
        #newdummy.to_csv(filename, mode = "w")

    print("finish")

def get_delta():
    dev_list = [
        "84:2e:27:6b:53:df",
        "3c:a0:67:85:86:1b",
        "94:d7:71:fc:67:c9",
        "f8:e6:1a:f1:d6:49",
        "00:f4:6f:9e:c6:eb"
    ]
    csvname = "1118 to 1122_total_day"
    dev_name = []
    ap_name = []
    data_list = []
    data_size = []
    deltatime = []
    deltaseq = []

    for dev in dev_list:
        for i in range(5):
            dev_bssid = dev.replace(":","_")

            ospath = "./separated/"+csvname+"/"+dev_bssid
            filename = ospath +"/"+dev_bssid+"_"+str(i)+".csv"

            dev_name.append(filename)

            df = pd.read_csv(filename)
            data_list.append(df)
            data_size.append(len(df))
            deltatime.append(df["timedifference"])
            deltaseq.append(df["sequence no"])

    dt = []
    ds = []
    for t, s in zip(deltatime,deltaseq):
        temp1 = []
        temp2 = []
        for i in range(len(t)):
            temp1.append(t[i]-t[0])
            temp2.append(s[i]-s[0])
        dt.append(temp1)
        ds.append(temp2)

    return dt, ds, dev_name

def tensor_linear_regression(dt, ds, dev_name):
    tf.disable_v2_behavior()

    W = tf.Variable(tf.random_normal([1]))
    b = tf.Variable(tf.random_normal([1]))

    X = tf.placeholder(tf.float32, shape=[None])
    Y = tf.placeholder(tf.float32, shape=[None])

    hypothesis = X*W+b

    cost = tf.reduce_mean(tf.square(hypothesis-Y))

    optimizer = tf.train.GradientDescentOptimizer(learning_rate=0.00000000001)
    train = optimizer.minimize(cost)
    pattern = []
    pred = []
    costt = []
    sess = tf.Session()

    for i in range(len(dev_name)):
        sess.run(tf.global_variables_initializer())
        tempcost = []
        for step in range(501):
            _, cost_val, W_val, b_val = sess.run([train,cost,W,b], feed_dict = {X:dt[i], Y:ds[i]})
            tempcost.append(W_val)
        print(dev_name[i],step, W_val, cost_val)
        pattern.append(W_val)
        pred.append(W_val*ds[i]+b_val)
        costt.append(tempcost)

    f = open("probe_NewDataProbe_total_training5.txt","w")
    for i in pattern:
        f.write(str(i[0]))
        f.write(",")
    f.close()

    
prepro_seq()
dt, ds, dev_name = get_delta()
tensor_linear_regression(dt,ds,dev_name)