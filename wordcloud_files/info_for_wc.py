import pymorphy3
from nltk.collocations import BigramCollocationFinder
from nltk.metrics import BigramAssocMeasures
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from db import data


def preprocess_p(text, stop_words, punctuation_marks, morph):
    text = text.replace('.', ' ')
    tokens = word_tokenize(text.lower())
    preprocessed_text = []
    for token in tokens:
        if token not in punctuation_marks:
            lemma = token
            if lemma not in stop_words:
                preprocessed_text.append(lemma)
    return preprocessed_text


def preprocess_w(text, stop_words, punctuation_marks, morph):
    text = text.replace('.', ' ')
    tokens = word_tokenize(text.lower())
    preprocessed_text = []
    for token in tokens:
        if token not in punctuation_marks:
            lemma = morph.parse(token)[0].normal_form
            if lemma not in stop_words:
                preprocessed_text.append(lemma)
    return preprocessed_text


punctuation_marks = ['!', ',', '(', ')', ':', '-', '?', '.', '..',
                     '...', '«', '»', ';', '–', '--']
stop_words = stopwords.words("russian") + ['всё', 'это']
morph = pymorphy3.MorphAnalyzer()

text = ''

for row in data:
    txt = str(row[0])
    text = text + ' ' + txt
preprocessed_w = preprocess_w(text, stop_words, punctuation_marks, morph)
for word in preprocessed_w:
    if preprocessed_w.count(word) < 3:
        preprocessed_w.remove(word)


preprocessed_p = []
preprocessed_text = preprocess_p(text, stop_words, punctuation_marks, morph)
finder = BigramCollocationFinder.from_words(preprocessed_text)

phrases = finder.nbest(BigramAssocMeasures.likelihood_ratio, 20)
ngram_freq = finder.ngram_fd
for bigram in phrases:
    total_phrase = bigram[0] + ' ' + bigram[1]
    frequency = ngram_freq[bigram]
    for i in range(frequency):
        preprocessed_p.append(total_phrase)
print(preprocessed_w + preprocessed_p)
