import numpy as np
import pandas as pd


from tensorflow.keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.models import load_model


reg_dict = {
    0: "Тульская область",
    1: "Калужская область",
    2: "Москва"
}
def label_to_reg(label):
    return reg_dict[label]


data = pd.read_csv('data.csv', header= None, sep = ';')

X = data[0].values
Y = data[1].values

tokenizer = Tokenizer()
tokenizer.fit_on_texts(X)


test = ["Москва круче всего", "Люблю калужскую область", "Тула лучше всех"]


test_seq = tokenizer.texts_to_sequences(test)
Xtest = pad_sequences(test_seq, maxlen = 10, padding = 'post', truncating = 'post')

model = load_model('my_model.h5')

y_pred = model.predict(Xtest)
y_pred = np.argmax(y_pred, axis = 1)

for i in range(len(test)):
    print(test[i], '   ', label_to_reg(y_pred[i]))