
import csv
from sklearn.linear_model import LinearRegression
import numpy as np
import prePro

#todo x_train 데이터를 모아야함
def make_timeRelative_list(csvFile):
    time_list = []
    with open(csvFile,"r") as f:
        rdr = csv.reader(f)
        temp_timelist = prePro.extract_data_index(rdr,1)
        
        for time in temp_timelist:
            time_list.append([time])
    return time_list

#시퀀스 넘버 증가량 리스트를 만든다.
def make_seqNumberList(csvFile):
    seqNum_0 = 0
    seqNum_list = []
    
    with open(csvFile,"r") as f:
        rdr = csv.reader(f)
        temp_seqNum_list = prePro.extract_data_index(rdr,2)  

        if temp_seqNum_list!=[]:
            seqNum_0 = float(temp_seqNum_list[0])
            for idx in range(len(temp_seqNum_list)):
                    seqNum_list.append([(float(temp_seqNum_list[idx]) - seqNum_0)])
            
    
    return seqNum_list

#문자열 실수 리스트를 정수형 리스트로 변경
def train_preProcessor(train):
    for idx in range(len(train)):
        train[idx] = int(float(train[idx]))

#선형 모델 기울기 반환
def linear_regreesion(x_train,y_train):
    X = np.array(x_train).astype(np.float64)
    y = np.array(y_train).astype(np.float64)

    line_fitter = LinearRegression()
    line_fitter.fit(X,y)
    
    
    return line_fitter.coef_
