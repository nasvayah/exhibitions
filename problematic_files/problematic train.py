import pandas as pd
import numpy as np
import pymorphy3
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from collections import Counter
import joblib

max_words = 10000
random_state = 42

#далее изменить название csv файла, если потребуется
banks = pd.read_csv('problem.csv', sep=',', index_col='id');

def preprocess(text, stop_words, punctuation_marks, morph):
    tokens = word_tokenize(text.lower())
    preprocessed_text = []
    for token in tokens:
        if token not in punctuation_marks:
            lemma = morph.parse(token)[0].normal_form
            if lemma not in stop_words:
                preprocessed_text.append(lemma)
    return preprocessed_text

punctuation_marks = ['!', ',', '(', ')', ':', '-', '?', '.', '..', '...', '«', '»', ';', '–', '--']
stop_words = stopwords.words("russian")
morph = pymorphy3.MorphAnalyzer()

banks['Preprocessed_texts'] = banks.apply(lambda row: preprocess(row['text'], punctuation_marks, stop_words, morph), axis=1)

words = Counter()
for txt in banks['Preprocessed_texts']:
    words.update(txt)

# Словарь, отображающий слова в коды
word_to_index = dict()
# Словарь, отображающий коды в слова
index_to_word = dict()

for i, word in enumerate(words.most_common(max_words - 2)):
    word_to_index[word[0]] = i + 2
    index_to_word[i + 2] = word[0]

def text_to_sequence(txt, word_to_index):
    seq = []
    for word in txt:
        index = word_to_index.get(word, 1) # 1 означает неизвестное слово
        # Неизвестные слова не добавляем в выходную последовательность
        if index != 1:
            seq.append(index)
    return seq

banks['Sequences'] = banks.apply(lambda row: text_to_sequence(row['Preprocessed_texts'], word_to_index), axis=1)

mapping = {'PROBLEM': 0, 'SIMPLE': 1}


banks.replace({'score': mapping}, inplace=True)


train = banks

x_train_seq = train['Sequences']
y_train = train['score']

def vectorize_sequences(sequences, dimension=10000):
    results = np.zeros((len(sequences), dimension))
    for i, sequence in enumerate(sequences):
        for index in sequence:
            results[i, index] += 1.
    return results

x_train = vectorize_sequences(x_train_seq, max_words)

lr = LogisticRegression(random_state=random_state, max_iter=500)

lr.fit(x_train, y_train)

#прописать путь до модели
joblib.dump(lr, 'logistic_regression_model.pkl')