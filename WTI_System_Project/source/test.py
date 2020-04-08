#reference : https://github.com/hunkim/DeepLearningZeroToAll/blob/master/lab-02-2-linear_regression_feed.py

import tensorflow as tf

tf.set_random_seed(777)  # for reproducibility

# training data
x_train = [22/10,95/10,95/10,102/10,102/10]    #수신시간
y_train = [0,7359/10,7360/10,7385/10,7386/10]   #시퀀스넘버

#x_train = [1,2,3]
#y_train = [1,2,3]

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

    print("x_train : ",x_train)
    print("y_train : ",y_train)
    # Fit the line
    for step in range(2001):
        _, cost_val, W_val, b_val = sess.run(
            [train, cost, W, b], feed_dict={X: x_train, Y: y_train}
        )
        if step % 20 == 0:
            print("step : ",step,"cost : ",cost_val,"w : ",W_val,"b : ", b_val)
        

    print("기울기 : ",W_val)