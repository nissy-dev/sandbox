import pickle
import csv
import time
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.model_selection import train_test_split
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.layers import LSTM, Embedding, Bidirectional, Dense, GRU
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction


# コードはこっちを見た方がいい
# 学習遅かったし、tensorがnumpyにどうしても変更できなかったので降参...
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


### 出力用関数 ###
def get_raw_contents(dataset, num, bos_id, eos_id):
    result = []
    for index in dataset[num]:
        if index == eos_id:
            break
            
        result.append(index)
        
        if index == bos_id:
            result = []
            
    return result


### Atenttion ###
class Attention(tf.keras.Model):
  def __init__(self, units):
    super(Attention, self).__init__()
    self.W1 = Dense(units)
    self.W2 = Dense(units)
    self.V = Dense(1)

  def call(self, query, values):
    # hidden shape == (batch_size, hidden size)
    # hidden_with_time_axis shape == (batch_size, 1, hidden size)
    # we are doing this to perform addition to calculate the score
    hidden_with_time_axis = tf.expand_dims(query, 1)

    # score shape == (batch_size, max_length, 1)
    # we get 1 at the last axis because we are applying score to self.V
    # the shape of the tensor before applying self.V is (batch_size, max_length, units)
    score = self.V(tf.nn.tanh(
        self.W1(values) + self.W2(hidden_with_time_axis)))

    # attention_weights shape == (batch_size, max_length, 1)
    attention_weights = tf.nn.softmax(score, axis=1)

    # context_vector shape after sum == (batch_size, hidden_size)
    context_vector = attention_weights * values
    context_vector = tf.reduce_sum(context_vector, axis=1)

    return context_vector, attention_weights


### Encoder ####
class Encoder(tf.keras.Model):
  def __init__(self, vocab_size, emb_dim, encoder_units, batch_size):
    super(Encoder, self).__init__()
    self.batch_size = batch_size
    self.encoder_units = encoder_units
    self.embedding = Embedding(vocab_size, emb_dim)
    self.gru = GRU(self.encoder_units, return_sequences=True, return_state=True)

  def call(self, x, hidden):
    x = self.embedding(x)
    output, state = self.gru(x, initial_state = hidden)
    return output, state

  def initialize_hidden_state(self):
    return tf.zeros([self.batch_size, self.encoder_units])


#### Decoder #### 
class Decoder(tf.keras.Model):
  def __init__(self, vocab_size, emb_dim, decoder_units, batch_size):
    super(Decoder, self).__init__()
    self.batch_size = batch_size
    self.decoder_units = decoder_units
    self.embedding = Embedding(vocab_size, emb_dim)
    self.gru = GRU(self.decoder_units, return_sequences=True, return_state=True)
    self.fc = Dense(vocab_size)

    # used for attention
    self.attention = Attention(self.decoder_units)

  def call(self, x, hidden, encoder_output):
    # enc_output shape == (batch_size, max_length, hidden_size)
    context_vector, attention_weights = self.attention(hidden, encoder_output)

    # x shape after passing through embedding == (batch_size, 1, embedding_dim)
    x = self.embedding(x)

    # x shape after concatenation == (batch_size, 1, embedding_dim + hidden_size)
    x = tf.concat([tf.expand_dims(context_vector, 1), x], axis=-1)

    # passing the concatenated vector to the GRU
    output, state = self.gru(x)

    # output shape == (batch_size * 1, hidden_size)
    output = tf.reshape(output, (-1, output.shape[2]))

    # output shape == (batch_size, vocab)
    x = self.fc(output)

    return x, state, attention_weights


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
x_train, x_valid, t_train, t_valid = train_test_split(x_train, t_train, test_size=0.1, random_state=42)
# データ(レビュー)の長さでソート (長い順)
x_train_lens = [len(com) for com in x_train]
sorted_train_indexes = sorted(range(len(x_train_lens)), key=lambda x: -x_train_lens[x])
x_train = [x_train[ind] for ind in sorted_train_indexes]
t_train = [t_train[ind] for ind in sorted_train_indexes]

# データの長さを全て統一する
x_train = pad_sequences(x_train, padding='post', value=0)
t_train = pad_sequences(t_train, padding='post', value=0)
t_test = pad_sequences(t_test, padding='post', value=0)

# データをバッチに変換
batch_size = 400
dataset = tf.data.Dataset.from_tensor_slices((x_train, t_train)).shuffle(len(x_train))
dataset = dataset.batch(batch_size, drop_remainder=True)
example_input_batch, example_target_batch = next(iter(dataset))


### Build model ###
emb_dim = 128
hid_dim = 256
att_dim = 128
encoder = Encoder(en_vocab_size, emb_dim, hid_dim, batch_size)
decoder = Decoder(ja_vocab_size, emb_dim, hid_dim, batch_size)


### Objective function ###
optimizer = tf.keras.optimizers.Adam()
# labelがone-hot形式でない場合に使う
loss_object = tf.keras.losses.SparseCategoricalCrossentropy(
    from_logits=True, reduction='none')

def loss_function(real, pred):
  mask = tf.math.logical_not(tf.math.equal(real, 0))
  loss_ = loss_object(real, pred)

  mask = tf.cast(mask, dtype=loss_.dtype)
  loss_ *= mask

  return tf.reduce_mean(loss_)


### Train ###
@tf.function
def train_step(inp, targ, enc_hidden):
  loss = 0

  with tf.GradientTape() as tape:
    enc_output, enc_hidden = encoder(inp, enc_hidden)
    dec_hidden = enc_hidden
    dec_input = tf.expand_dims([tokenizer_ja.word_index['<s>']] * batch_size, 1)

    # Teacher forcing - feeding the target as the next input
    for t in range(1, targ.shape[1]):
      # passing enc_output to the decoder
      predictions, dec_hidden, _ = decoder(dec_input, dec_hidden, enc_output)

      loss += loss_function(targ[:, t], predictions)

      # using teacher forcing
      dec_input = tf.expand_dims(targ[:, t], 1)

  batch_loss = (loss / int(targ.shape[1]))

  variables = encoder.trainable_variables + decoder.trainable_variables

  gradients = tape.gradient(loss, variables)

  optimizer.apply_gradients(zip(gradients, variables))

  return batch_loss


#### 以下から実際の実行処理 ####
sess = tf.Session()
sess.run(tf.global_variables_initializer())

#### Training ####
with sess.as_default():
    epochs = 10
    steps_per_epoch = len(x_train) // batch_size
    for epoch in range(epochs):
      start = time.time()
    
      enc_hidden = encoder.initialize_hidden_state()
      total_loss = 0
    
      for (batch, (inp, targ)) in enumerate(dataset.take(steps_per_epoch)):
        print(batch)
        batch_loss = train_step(inp, targ, enc_hidden)
        total_loss += batch_loss
    
        if batch % 100 == 0:
            print('Epoch {} Batch {} Loss {:.4f}'.format(epoch + 1, batch, batch_loss.eval()))
    
      print('Epoch {} Loss {:.4f}'.format(epoch + 1,
                                          total_loss / steps_per_epoch))
      print('Time taken for 1 epoch {} sec\n'.format(time.time() - start))


### Translate...? ###
def translate(x_test):
    inputs = tf.convert_to_tensor(x_test)
    hidden = [tf.zeros((1, units))]
    enc_out, enc_hidden = encoder(inputs, hidden)
    
    dec_hidden = enc_hidden
    dec_input = tf.expand_dims([tokenizer_ja.word_index['<s>']], 0)
    predictions, dec_hidden, attention_weights = decoder(dec_input, dec_hidden, enc_out)
    result = [get_raw_contents(predictions, i, bos_id_ja, eos_id_ja) for i in range(len(predictions))]
    return result

result = translate(x_test)
output = sess.run(result)
