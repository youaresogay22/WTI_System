
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
                if time_list[idx]==0:
                    time_list[idx] = int(float(time_list[idx]))
                else:
                    time_list[idx] = (int(float(time_list[idx]))/10)
                
        
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
                if seqNum_list[idx]==0:
                    seqNum_list[idx] = int(seqNum_list[idx]) - seqNum_0
                else:
                    seqNum_list[idx] = (int(seqNum_list[idx]) - seqNum_0)/10
                
    return seqNum_list

#문자열 실수 리스트를 정수형 리스트로 변경
def train_preProcessor(train):
    for idx in range(len(train)):
        train[idx] = int(float(train[idx]))

def linear_regreesion(x_train,y_train):
    #x_train_p, y_train_p 매개변수는 입력받은 수신시간과 패킷 데이터리스트이나
    #임시적으로 사용을 하지 않고 있습니다.

    # training data
    #x_train = [22,95,95,102,102]
    #y_train = [0,7359,7360,7385,7386]

    #x_train = [1,2,3]
    #y_train = [1,2,3]

    tf.set_random_seed(777)  # for reproducibility

    # Try to find values for W and b to compute Y = W * X + b
    W = tf.Variable(tf.random_normal([1]), name="weight")
    b = tf.Variable(tf.random_normal([1]), name="bias")

    # placeholders for a tensor that will be always fed using feed_dict
    X = tf.placeholder(tf.float32, shape=[None])
    Y = tf.placeholder(tf.float32, shape=[None])

    # Our hypothesis is X * W + b
    hypothesis = X * W + b

    # cost/loss function
    cost = tf.reduce_mean(tf.square(hypothesis - Y))

    # optimizer
    train = tf.train.GradientDescentOptimizer(learning_rate=0.01).minimize(cost)

    # Launch the graph in a session.
    with tf.Session() as sess:
        # Initializes global variables in the graph.
        sess.run(tf.global_variables_initializer())

        # Fit the line
        for step in range(2001):
            _, cost_val, W_val, b_val = sess.run(
                [train, cost, W, b], feed_dict={X: x_train, Y: y_train}
            )
            #if step % 20 == 0:
            #   print(step, cost_val, W_val, b_val)
    
    return W_val[0]