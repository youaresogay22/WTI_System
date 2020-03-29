
import csv
import extract
import tensorflow as tf
#todo x_train 데이터를 모아야함
def make_timeRelative_list(csvFile):
    with open(csvFile,"r") as f:
        rdr = csv.reader(f)
        time_list = extract.extract_data_index(rdr,1)

        if time_list!=[]:
            for idx in range(len(time_list)):
                time_list[idx] = int(float(time_list[idx]))
        
        return time_list

#시퀀스 넘버 증가량 리스트를 만든다.
def make_seqNumberList(csvFile):
    seqNum_0 = 0
    seqNum_list = []

    with open(csvFile,"r") as f:
        rdr = csv.reader(f)
        seqNum_list = extract.extract_data_index(rdr,2)  

        if seqNum_list!=[]:
            seqNum_0 = int(seqNum_list[0])
            for idx in range(len(seqNum_list)):
                seqNum_list[idx] = int(seqNum_list[idx]) - seqNum_0    
    return seqNum_list

#문자열 실수 리스트를 정수형 리스트로 변경
def train_preProcessor(train):
    for idx in range(len(train)):
        train[idx] = int(float(train[idx]))

def linear_regreesion(x_train,y_train):
    print(x_train)
    print(y_train)
    w = tf.Variable(tf.random_normal([1]),name="weight")
    b = tf.Variable(tf.random_normal([1]),name="bias")
    X = tf.placeholder(tf.float32, shape=[None])
    Y = tf.placeholder(tf.float32, shape=[None])
    

    #Our hypothesis XW + b
    hypothesis = X * w + b

    #cost / loss function
    cost = tf.reduce_mean(tf.square(hypothesis-Y))

    #minimize
    optimizer  = tf.train.GradientDescentOptimizer(learning_rate=0.01)
    train =optimizer.minimize(cost)

    #Launch the graph in a session
    sess = tf.Session()

    #Initializes global variables in the graph
    sess.run(tf.global_variables_initializer())

    #Fit the line
    for step in range(2001):
        cost_val, W_val, b_val, _ = sess.run([cost,w,b,train],
                                                    feed_dict={X:x_train,
                                                                        Y:y_train})
        if step % 20 ==0:
            print(step, cost_val, W_val, b_val)


    for idx in range(len(x_train)):
        print(sess.run(hypothesis,feed_dict={X:[x_train[idx]]}))

    return sess, hypothesis

