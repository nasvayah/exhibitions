import pandas as pd
import numpy as np
import pymorphy3
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import Counter
import joblib
from OSRus import conn

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


#далее изменить название csv файла, если потребуется
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
                                                                    # прописать путь до модели
    lr = joblib.load('logistic_regression_model.pkl')
    result = lr.predict(bow)
    return int(result[0])



#изменить скрипт
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
        probl+=1            #изменить скрипт
        update_query = f""" update sandbox.res1 
        set score = 'PROBLEM'
        where question_answer = '{text}'
        """
    elif 1 == res:
        simp+=1             #изменить скрипт
        update_query = f""" update sandbox.res1
        set score = 'SIMPLE'
        where question_answer = '{text}'
        """

    conn.execute(update_query)
    conn.commit()