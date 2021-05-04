import pickle
import csv
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.model_selection import train_test_split
from tensorflow.keras.preprocessing.sequence import pad_sequences
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction

# コードはこっちを見た方がいい
# https://github.com/tensorflow/docs/blob/master/site/en/r2/tutorials/text/nmt_with_attention.ipynb
def pickle_load(path):
    with open(path, 'rb') as f:
        data = pickle.load(f)
    return data


def load_data():
    # save np.load
    np_load_old = np.load
    # modify the default parameters of np.load (work around)
    np.load = lambda *a,**k: np_load_old(*a, allow_pickle=True, **k)

    # 学習データ
    x_train = pickle_load('./x_train.pkl')
    t_train = pickle_load('./t_train.pkl')
    tokenizer_en = np.load('./tokenizer_en.npy').item()
    tokenizer_ja = np.load('./tokenizer_ja.npy').item()

    # テストデータ
    x_test = pickle_load('./x_test.pkl')

    # restore the np.load
    np.load = np_load_old
    return (x_train, t_train, tokenizer_en, tokenizer_ja, x_test)


def tf_log(x):
    return tf.log(tf.clip_by_value(x, 1e-10, x))


### 出力用関数 ###
def get_raw_contents(dataset, num, bos_id, eos_id):
    """convert vector to sentence

    Parameters
    ----------
    dataset : 
    num : 
    bos_id : 文頭を表す <s> のid
    eos_id : 文末を表す </s> のid
    """
    result = []
    for index in dataset[num]:
        if index == eos_id:
            break
            
        result.append(index)
        
        if index == bos_id:
            result = []
            
    return result


### Embedding ###
class Embedding:
    def __init__(self, vocab_size, emb_dim, scale=0.08):
        # 各単語IDに対する特徴量ベクトルを作成
        self.V = tf.Variable(tf.random_normal([vocab_size, emb_dim], stddev=scale), name='V')

    def __call__(self, x):
        # self.Vから入力された文に対応するデータを取り出す
        return tf.nn.embedding_lookup(self.V, x)


### LSTM ####
class LSTM:
    """LSTM Class like Keras"""
    def __init__(self, hid_dim, seq_len, initial_state, is_training, return_state = False, return_sequences = False, hold_state = False, name = None):
        self.cell = tf.nn.rnn_cell.BasicLSTMCell(hid_dim)
        self.initial_state = initial_state
        self.seq_len = seq_len
        self.return_state = return_state
        self.return_sequences = return_sequences
        self.hold_state = hold_state
        self.name = name
        self.is_training = is_training

    def __call__(self, x):
        with tf.variable_scope(self.name):
            keep_prob = tf.cond(self.is_training, lambda:tf.constant(0.7), lambda:tf.constant(1.0))
            self.cell = tf.contrib.rnn.DropoutWrapper(self.cell, input_keep_prob=keep_prob)
            outputs, state = tf.nn.dynamic_rnn(self.cell, x, self.seq_len, self.initial_state)
        
        if self.hold_state:
            self.initial_state = state
        
        # 返り値を変えたい時があるので振り分け
        if not self.return_sequences:
            outputs = state.h
            
        if not self.return_state:
            return outputs
        
        return outputs, state


#### Attention ####
# ref: https://qiita.com/halhorn/items/c91497522be27bde17ce
class Attention:
    def __init__(self, hid_dim, out_dim, enc_out, seq_len):
        e_hid_dim, d_hid_dim = hid_dim, hid_dim

        # self.enc_out: [batch_size, enc_length, e_hid_dim]
        self.enc_out = enc_out
        self.seq_len = seq_len
        glorot_a = tf.cast(tf.sqrt(6/(e_hid_dim + d_hid_dim)), tf.float32)
        # self.W_a  : [e_hid_dim, d_hid_dim]
        self.W_a  = tf.Variable(tf.random_uniform([e_hid_dim, d_hid_dim], minval=-glorot_a, maxval=glorot_a), name='W_a')
        
        glorot_c = tf.cast(tf.sqrt(6/(e_hid_dim + d_hid_dim + out_dim)), tf.float32)
        self.W_c = tf.Variable(tf.random_uniform([e_hid_dim+d_hid_dim, out_dim], minval=-glorot_c, maxval=glorot_c), name='W_c')
        self.b    = tf.Variable(np.zeros([out_dim]).astype('float32'), name='b')
        
    def __call__(self, dec_out):
        # -> enc_out: [batch_size, enc_length, d_hid_dim]
        W_a_broadcasted = tf.tile(tf.expand_dims(self.W_a, axis=0), [tf.shape(self.enc_out)[0],1,1])
        enc_out = tf.matmul(self.enc_out, W_a_broadcasted)
        
        # dec_out: [batch_size, dec_length, d_hid_dim]
        # -> score: [batch_size, dec_length, enc_length]
        # ここがqueryとkeyの内積 (Attention score)
        score = tf.matmul(dec_out, tf.transpose(enc_out, perm=[0,2,1]))
        
        # encoderのステップにそって正規化する(softmax)
        score = score - tf.reduce_max(score, axis=-1, keep_dims=True) # for numerically stable softmax
        mask = tf.cast(tf.sequence_mask(self.seq_len, tf.shape(score)[-1]), tf.float32)
        exp_score = tf.exp(score) * tf.expand_dims(mask, axis=1)
        # self.a  : [batch_size, dec_length, enc_length]
        # attention weightの算出
        self.a = exp_score / tf.reduce_sum(exp_score, axis=-1, keep_dims=True)

        # -> c: [batch_size, dec_length, e_hid_dim]
        # 重みからvalueを抽出
        c = tf.matmul(self.a, self.enc_out) # Context vector

        # output算出
        W_c_broadcasted = tf.tile(tf.expand_dims(self.W_c, axis=0), [tf.shape(c)[0],1,1])
        return tf.nn.tanh(tf.matmul(tf.concat([c, dec_out], -1), W_c_broadcasted) + self.b)


def calc_loss(y, t):
    """caluculate loss value"""
    cost = -tf.reduce_mean(tf.reduce_sum(t * tf_log(y[:, :-1]), axis=[1, 2]))
    return cost


def training(cost):
    """defined the optimizer"""
    # use Gradient Clipping
    optimizer = tf.train.AdamOptimizer()
    grads = optimizer.compute_gradients(cost)
    clipped_grads = [(tf.clip_by_value(grad_val, -1., 1.), var) for grad_val, var in grads]
    train = optimizer.apply_gradients(clipped_grads)
    return train


### データの読み込み ###
x_train, t_train, tokenizer_en, tokenizer_ja, x_test = load_data()
# IDと対応する単語のMapを取得
detokenizer_en = dict(map(reversed, tokenizer_en.word_index.items()))
detokenizer_ja = dict(map(reversed, tokenizer_ja.word_index.items()))
# 単語数を取得
en_vocab_size = len(tokenizer_en.word_index) + 1
ja_vocab_size = len(tokenizer_ja.word_index) + 1
# 文頭と文末を表すidを取得しておく
bos_id_ja, eos_id_ja = tokenizer_ja.texts_to_sequences(['<s> </s>'])[0]
# Validの準備
x_train, x_valid, t_train, t_valid = train_test_split(x_train, t_train, test_size=0.2, random_state=42)
# データ(レビュー)の長さでソート (長い順)
x_train_lens = [len(com) for com in x_train]
sorted_train_indexes = sorted(range(len(x_train_lens)), key=lambda x: -x_train_lens[x])
x_train = [x_train[ind] for ind in sorted_train_indexes]
t_train = [t_train[ind] for ind in sorted_train_indexes]


### ハイパーパラメーター ###
pad_index = 0 ## ほぼ固定
emb_dim = 256
hid_dim = 1024
att_dim = 1024
n_epochs = 2
batch_size = 100
dropout = 0.3


n_batches_train = len(x_train) // batch_size
n_batches_valid = len(x_valid) // batch_size
tf.reset_default_graph()
with tf.Session() as sess:
    #### Seq2Seq modelの処理 ####
    x = tf.placeholder(tf.int32, [None, None], name='x')
    t = tf.placeholder(tf.int32, [None, None], name='t')
    is_training = tf.placeholder(tf.bool)
    # データ長さの取得
    seq_len = tf.reduce_sum(tf.cast(tf.not_equal(x, pad_index), tf.int32), axis=1)
    seq_len_t_in = tf.reduce_sum(tf.cast(tf.not_equal(t, pad_index), tf.int32), axis=1) - 1
    # 出力の整形
    t_out = tf.one_hot(t[:, 1:], depth=ja_vocab_size, dtype=tf.float32)
    t_out = t_out * tf.expand_dims(tf.cast(tf.not_equal(t[:, 1:], pad_index), tf.float32), axis=-1)
    # init state
    initial_state = tf.nn.rnn_cell.LSTMStateTuple(tf.zeros([tf.shape(x)[0], hid_dim]), tf.zeros([tf.shape(x)[0], hid_dim]))
    # Encoder
    h_e = Embedding(en_vocab_size, emb_dim)(x)
    h_e = tf.layers.dropout(h_e, dropout, is_training)
    encoded_outputs, encoded_state = LSTM(hid_dim, seq_len, initial_state, is_training, return_sequences=True, return_state=True, name='encoder_lstm_a')(h_e)
    # Decoder
    decoder = [
        Embedding(ja_vocab_size, emb_dim),
        LSTM(hid_dim, seq_len_t_in, encoded_state, is_training, return_sequences=True, name='decoder_lstm_a'),
        Attention(hid_dim, att_dim, encoded_outputs, seq_len),
        tf.layers.Dense(ja_vocab_size, tf.nn.softmax)
    ]
    h_d = decoder[0](t)
    h_d = tf.layers.dropout(h_d, dropout, is_training)
    h_d = decoder[1](h_d)
    h_d = tf.layers.dropout(h_d, dropout, is_training)
    h_d = decoder[2](h_d)
    h_d = tf.layers.dropout(h_d, dropout, is_training)
    y = decoder[3](h_d)

    cost = calc_loss(y, t_out)
    train = training(cost)

    #### 学習 ####
    init = tf.global_variables_initializer()
    sess.run(init)
    for epoch in range(n_epochs):
        train_costs = []
        for i in range(n_batches_train):
            start = i * batch_size
            end = start + batch_size
            x_train_batch = np.array(pad_sequences(x_train[start:end], padding='post', value=pad_index))
            t_train_batch = np.array(pad_sequences(t_train[start:end], padding='post', value=pad_index))
            feed_dict = {
                x: x_train_batch, 
                t: t_train_batch,
                is_training: True
            }
            _, train_cost = sess.run([train, cost], feed_dict)
            train_costs.append(train_cost)
        
        # Valid
        valid_costs = []
        for i in range(n_batches_valid):
            start = i * batch_size
            end = start + batch_size
            x_valid_pad = np.array(pad_sequences(x_valid[start:end], padding='post', value=pad_index))
            t_valid_pad = np.array(pad_sequences(t_valid[start:end], padding='post', value=pad_index))
            feed_dict = {
                x: x_valid_pad, 
                t: t_valid_pad,
                is_training: False
            }
            valid_cost = sess.run(cost, feed_dict)
            valid_costs.append(valid_cost)
        print('EPOCH: %i, Training Cost: %.3f, Validation Cost: %.3f' % (epoch+1, np.mean(train_costs), valid_cost))


    #### 翻訳文の生成 ####
    # ここは解読無理....
    bos_eos = tf.placeholder(tf.int32, [2], name='bos_eos')
    max_len = tf.placeholder(tf.int32, name='max_len') # iterationの繰り返し回数の限度
    
    def cond(t, continue_flag, init_state, seq_last, seq, att):
        unfinished = tf.not_equal(tf.reduce_sum(tf.cast(continue_flag, tf.int32)), 0)
        return tf.logical_and(t < max_len, unfinished)
    
    def body(t, prev_continue_flag, init_state, seq_last, seq, att):
        decoder[1].initial_state = init_state
        
        # Decoderグラフを再構築
        h = decoder[0](tf.expand_dims(seq_last, -1))
        h = decoder[1](h)
        h = decoder[2](h)
        y = decoder[3](h)
        
        seq_t = tf.reshape(tf.cast(tf.argmax(y, axis=2), tf.int32), shape=[-1])
        next_state = decoder[1].initial_state
        
        continue_flag = tf.logical_and(prev_continue_flag, tf.not_equal(seq_t, bos_eos[1])) # flagの更新
        
        return [t+1, continue_flag, next_state, seq_t, seq.write(t, seq_t), att.write(t-1, tf.squeeze(decoder[2].a))]

    decoder[1].hold_state = True
    decoder[1].seq_len = None
    
    seq_0 = tf.ones([tf.shape(x)[0]], tf.int32)*bos_eos[0]
    
    t_0 = tf.constant(1)
    f_0 = tf.cast(tf.ones_like(seq_0), dtype=tf.bool) # バッチ内の各系列で</s>が出たかどうかの未了flag(0:出た, 1:出てない)
    seq_array = tf.TensorArray(dtype=tf.int32, size=1, dynamic_size=True).write(0, seq_0)
    att_array = tf.TensorArray(dtype=tf.float32, size=1, dynamic_size=True)
    
    *_, seq, att = tf.while_loop(cond, body, loop_vars=[t_0, f_0, encoded_state, seq_0, seq_array, att_array])
    
    res = (tf.transpose(seq.stack()), tf.transpose(att.stack(), perm=[1, 0, 2]))

    ### 今回の学習のスコアの算出
    y_valid_pred = []
    for i in range(n_batches_valid):
        start = i * batch_size
        end = start + batch_size
        x_valid_pad = np.array(pad_sequences(x_valid[start:end], padding='post', value=pad_index))
        y_valid_pred_tmp, att_weights = sess.run(res, feed_dict={
            x: x_valid_pad,
            bos_eos: np.array([bos_id_ja, eos_id_ja]),
            max_len: 100
        })
        y_valid_pred.append(y_valid_pred_tmp)

    bleu_score = []
    count = 0
    for i in range(n_batches_valid):
        y_pred = y_valid_pred[i]
        for num in range(len(y_pred)):
            content = get_raw_contents(y_pred, num, bos_id_ja, eos_id_ja)
            gen = [detokenizer_ja[com] for com in content]
            ref = [[detokenizer_ja[com] for com in t_valid[count][1:-1]]]
            score = sentence_bleu(ref, gen, smoothing_function=SmoothingFunction().method1)
            bleu_score.append(score)
            count += 1

    print("Valid Bleu Score : {}".format(np.mean(bleu_score)))

    # テストデータの出力
    n_batches_test = len(x_test) // batch_size
    y_test_pred = []
    for i in range(n_batches_test):
        start = i * batch_size
        end = start + batch_size
        x_test_pad = np.array(pad_sequences(x_test[start:end], padding='post', value=pad_index))
        y_pred, att_weights = sess.run(res, feed_dict={
            x: x_test_pad,
            bos_eos: np.array([bos_id_ja, eos_id_ja]),
            max_len: 100
        })
        y_test_pred.append(y_pred)

    result = []
    for i in range(n_batches_test):
        y_pred = y_test_pred[i]
        for num in range(len(y_pred)):
            content = get_raw_contents(y_pred, num, bos_id_ja, eos_id_ja)
            result.append(content)

    with open('./submission_gen.csv', 'w') as file:
        writer = csv.writer(file, lineterminator='\n')
        writer.writerows(result)
