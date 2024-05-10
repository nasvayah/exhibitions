import numpy as np
import pandas as pd

from keras.models import Sequential
from keras.layers import Dense, LSTM, SimpleRNN, Embedding
import tensorflow as tf

from tensorflow.keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.utils import to_categorical
from keras.models import load_model

from navec import Navec

path = 'navec_hudlit_v1_12B_500K_300d_100q.tar'
navec = Navec.load(path)


data = pd.read_csv('data.csv', header= None, sep = ';')
reg_dict = {
    0: "Тульская область",
    1: "Калужская область",
    2: "Москва"
}
def label_to_reg(label):
    return reg_dict[label]

X = data[0].values
Y = data[1].values

tokenizer = Tokenizer()
tokenizer.fit_on_texts(X)
word2index = tokenizer.word_index
Xtokens = tokenizer.texts_to_sequences(X)

def get_maxlen(data):
    maxlen = 0
    for sent in data:
        maxlen = max(maxlen, len(sent))
    return maxlen

maxlen = get_maxlen(Xtokens)

Xtrain = pad_sequences(Xtokens, maxlen = maxlen, padding = 'post', truncating = 'post')
Ytrain = to_categorical(Y)


embed_size = 300
embedding_matrix = np.zeros((len(word2index)+1, embed_size))

for word, i in word2index.items():
    embed_vector = navec[word]
    embedding_matrix[i] = embed_vector


#____________________обучение

# model = Sequential ([
#     Embedding(input_dim = len(word2index) + 1,
#               output_dim = embed_size,
#               input_length = maxlen,
#               weights = [embedding_matrix],
#               trainable = False),
#     LSTM(units=16, return_sequences=True),
#     LSTM(units=4),
#     Dense(3, activation='softmax')
# ])

# model.compile(optimizer = 'adam', loss = 'categorical_crossentropy', metrics = ['accuracy'])
# model.fit(Xtrain, Ytrain, epochs = 100)
#
# model.save('my_model.keras')



#________________тесты

model = load_model('my_model.h5')

test = ["Москва круче всего", "Люблю калужскую область", "Тула лучше всех", "Все", "хихихи москва"]

test_seq = tokenizer.texts_to_sequences(test)
Xtest = pad_sequences(test_seq, maxlen = maxlen, padding = 'post', truncating = 'post')

y_pred = model.predict(Xtest)
y_pred = np.argmax(y_pred, axis = 1)

for i in range(len(test)):
    print(test[i], '--------', label_to_reg(y_pred[i]))