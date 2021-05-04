import os
import gym
import numpy as np
import tensorflow as tf

from collections import deque

env = gym.make('MountainCar-v0')

tf.reset_default_graph()

n_states = 2
n_actions = 3

initializer = tf.variance_scaling_initializer()

x_state = tf.placeholder(tf.float32, [None, n_states])

def original_network(x):
    with tf.variable_scope('Original', reuse=tf.AUTO_REUSE):
        h = tf.layers.Dense(units=128, activation=tf.nn.elu, kernel_initializer=initializer)(x)
        h = tf.layers.Dense(units=128, activation=tf.nn.elu, kernel_initializer=initializer)(h)
        h = tf.layers.Dense(units=128, activation=tf.nn.elu, kernel_initializer=initializer)(h)
        h = tf.layers.Dense(units=128, activation=tf.nn.elu, kernel_initializer=initializer)(h)
        y = tf.layers.Dense(units=n_actions, kernel_initializer=initializer)(h)
    return y

def target_network(x):
    with tf.variable_scope('Target', reuse=tf.AUTO_REUSE):
        h = tf.layers.Dense(units=128, activation=tf.nn.elu, kernel_initializer=initializer)(x)
        h = tf.layers.Dense(units=128, activation=tf.nn.elu, kernel_initializer=initializer)(h)
        h = tf.layers.Dense(units=128, activation=tf.nn.elu, kernel_initializer=initializer)(h)
        y = tf.layers.Dense(units=n_actions, kernel_initializer=initializer)(h)
    return y

q_original = original_network(x_state)
vars_original = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope='Original')

q_target = target_network(x_state)
vars_target = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope='Target')

### weight copy operation ###
copy_ops = [var_target.assign(var_original) for var_target, var_original in zip(vars_target, vars_original)]
copy_weights = tf.group(*copy_ops)

### train ###
t = tf.placeholder(tf.float32, [None])
x_action = tf.placeholder(tf.int32, [None])
q_value = tf.reduce_sum(q_original * tf.one_hot(x_action, n_actions), axis=1)

cost = tf.reduce_mean(tf.square(tf.subtract(t,q_value)))
optimizer = tf.train.AdamOptimizer()
train_ops = optimizer.minimize(cost)


### create init memory ###
class ReplayMemory:
    def __init__(self, memory_size):
        self.memory_size = memory_size
        self.memory = deque([], maxlen = memory_size)
    
    def append(self, transition):
        self.memory.append(transition)
    
    def sample(self, batch_size):
        batch_indexes = np.random.randint(0, len(self.memory), size=batch_size).tolist()

        state      = np.array([self.memory[index]['state'] for index in batch_indexes])
        next_state = np.array([self.memory[index]['next_state'] for index in batch_indexes])
        reward     = np.array([self.memory[index]['reward'] for index in batch_indexes])
        action     = np.array([self.memory[index]['action'] for index in batch_indexes])
        terminal   = np.array([self.memory[index]['terminal'] for index in batch_indexes])
        
        return {'state': state, 'next_state': next_state, 'reward': reward, 'action': action, 'terminal': terminal}


memory_size = 50000 #メモリーサイズ
initial_memory_size = 500 #事前に貯める経験数
replay_memory = ReplayMemory(memory_size)

step = 0
while True:
    state = env.reset()
    terminal = False
    
    while not terminal:
        action = env.action_space.sample() # ランダムに行動を選択
        
        next_state, reward, terminal, _ = env.step(action) # 状態、報酬、終了判定の取得
        
        transition = {
            'state': state,
            'next_state': next_state,
            'reward': reward,
            'action': action,
            'terminal': int(terminal)
        }
        replay_memory.append(transition) # 経験の記憶

        state = next_state
        
        step += 1
    
    if step >= initial_memory_size:
        break


### epsilon greedy ####
eps_start = 1.0
eps_end = 0.1
n_steps = 10000
def get_eps(step):
    return max(0.1, (eps_end - eps_start) / n_steps * step + eps_start)

### train ###
gamma = 0.99
target_update_interval = 1000 #重みの更新間隔
batch_size = 64
n_episodes = 500
step = 0
init = tf.global_variables_initializer()

with tf.Session() as sess:
    init.run()
    copy_weights.run() # 初期重みのコピー
    for episode in range(n_episodes):
        state = env.reset()
        terminal = False

        total_reward = 0
        total_q_max = []
        while not terminal:
            q = q_original.eval(feed_dict={x_state: state[None]}) # Q値の計算
            total_q_max.append(np.max(q))

            eps = get_eps(step) # εの更新
            if np.random.random() < eps:
                action = env.action_space.sample() # （ランダムに）行動を選択
            else:
                action = np.argmax(q) # 行動を選択
            next_state, reward, terminal, _ = env.step(action) # 状態、報酬、終了判定の取得
            reward = np.sign(reward)
            total_reward += reward # エピソード内の報酬を更新

            transition = {
                'state': state,
                'next_state': next_state,
                'reward': reward,
                'action': action,
                'terminal': int(terminal)
            }
            replay_memory.append(transition) # 経験の記憶
            
            batch = replay_memory.sample(batch_size) # 経験のサンプリング
            q_target_next = q_target.eval(feed_dict={x_state: batch['next_state']}) # ターゲットQ値の計算
            t_value = batch['reward'] + (1 - batch['terminal']) * gamma * q_target_next.max(1)
            
            train_ops.run(feed_dict = {x_state: batch['state'], x_action: batch['action'], t: t_value}) # 訓練オペレーション

            state = next_state

            if (step + 1) % target_update_interval == 0:
                copy_weights.run() # 一定期間ごとに重みをコピー

            step += 1

        if (episode + 1) % 10 == 0:
            print('Episode: {}, Reward: {}, Q_max: {:.4f}, eps: {:.4f}'.format(episode + 1, total_reward, np.mean(total_q_max), eps))
    
    # 学習させたネットワークでTest
    frames = []
    state = env.reset()
    terminal = False

    total_reward = 0
    while not terminal:
        q = q_original.eval(feed_dict={x_state: state[None]})
        action = np.argmax(q)

        next_state, reward, terminal, _ = env.step(action)
        total_reward += reward

        state = next_state
    
    print('Test Reward:', total_reward)