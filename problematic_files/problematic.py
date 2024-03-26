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

def text_to_sequence(txt, word_to_index):
    seq = []
    for word in txt:
        index = word_to_index.get(word, 1) # 1 означает неизвестное слово
        # Неизвестные слова не добавляем в выходную последовательность
        if index != 1:
            seq.append(index)
    return seq

def vectorize_sequences(sequences, dimension=10000):
    results = np.zeros((len(sequences), dimension))
    for i, sequence in enumerate(sequences):
        for index in sequence:
            results[i, index] += 1.
    return results

banks = pd.read_csv('problem.csv', sep=',', index_col='id');
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


def result(text):
    preprocessed_text = preprocess(text, stop_words, punctuation_marks, morph)
    seq = text_to_sequence(preprocessed_text, word_to_index)
    bow = vectorize_sequences([seq], max_words)
    lr = joblib.load('logistic_regression_model.pkl')
    result = lr.predict(bow)
    return int(result[0])



import os.path
import psycopg2
from dotenv import load_dotenv

load_dotenv()

class DB:
    def __init__(self):
        self.conn = psycopg2.connect(host='rc1b-2im86q7efcxd3klt.mdb.yandexcloud.net',
                                     port='6432',
                                     user='ex_tg',
                                     password='rFW3sRYyph6xUJw',
                                     dbname='exhibition_db',
                                     sslmode='require')
        self.cur = self.conn.cursor()

    def execute(self, query):
        self.cur.execute(query)

    def fetch_all(self):
        return self.cur.fetchall()

    def close(self):
        self.cur.close()
        self.conn.close()
    def commit(self):
        self.conn.commit()

conn = DB()
query = """select
res1.question_answer
from sandbox.res1
where res1.question_answer notnull and res1.question_answer!='' and res1.question_answer!=' '
;"""
conn.execute(query)
data = conn.fetch_all()

i = 0
probl = 0
simp = 0
for row in data:
    text = str(row[0])
    i+=1
    print(i)
    res = result(text)
    print(text)
    print(res)
    if 0 == res:
        probl+=1
        update_query = f""" update sandbox.res1
        set score = 'PROBLEM'
        where question_answer = '{text}'
        """
    elif 1 == res:
        simp+=1
        update_query = f""" update sandbox.res1
        set score = 'SIMPLE'
        where question_answer = '{text}'
        """

    conn.execute(update_query)
    conn.commit()