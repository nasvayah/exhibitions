import pymorphy3
from nltk.collocations import BigramCollocationFinder
from nltk.metrics import BigramAssocMeasures
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import re
from psycopg2 import sql
#далее изменить на необходимые параметры подключения к бд в файле db.py
from OSRus import data, conn

def deEmojify(text):
    regrex_pattern = re.compile(pattern = "["
                                u"\U00000000-\U00000009"
                                u"\U0000000B-\U0000001F"
                                u"\U00000080-\U00000400"
                                u"\U00000402-\U0000040F"
                                u"\U00000450-\U00000450"
                                u"\U00000452-\U0010FFFF"
                                "]+", flags = re.UNICODE)
    return regrex_pattern.sub(r' ',text)


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
    text = deEmojify(text.replace('.', ' '))
    text = text.replace("'", ' ')
    tokens = word_tokenize(text.lower())
    preprocessed_text = []
    for token in tokens:
        if token not in punctuation_marks and token != "'":
            lemma = morph.parse(token)[0].normal_form
            if lemma not in stop_words:
                preprocessed_text.append(lemma)
    return preprocessed_text


punctuation_marks = ['!', ',', '(', ')', ':', '-', '?', '.', '..',
                     '...', '«', '»', ';', '–', '--', '<', '>', '=', '+', '\'']
stop_words = stopwords.words("russian") + ['всё', 'это']       #дополнить список, если нужно
morph = pymorphy3.MorphAnalyzer()

text = ''

for row in data:
    txt = str(row[3])
    id = row[0]
    question_name = row[1]
    date_create = str(row[2])
    mid_res = preprocess_w(txt, stop_words, punctuation_marks, morph)
    for word in mid_res:
        update_query = f"""
        insert into sandbox.frequency(id, question_name, date_create, word)
        values({id},'{question_name}','{date_create}','{word}');
        ;
        update sandbox.freq_old_id
        set max_id={id}
        where id = 1
        ;"""
        conn.execute(update_query)
        conn.commit()


query0 = """select
word, freq from sandbox.frequency
where freq is null
"""
conn.execute(query0)
data0 = conn.fetch_all()


wordcount_q = """select
count(*) from sandbox.frequency"""
conn.execute(wordcount_q)
data_q = conn.fetch_all()
for row in data_q:
    wordcount = int(str(row[0]))

for row in data0:
    word = str(row[0])
    text = text + ' ' + word

for row in data0:
    word = str(row[0])
    freq = row[1]
    value = text.count(word)*100 / wordcount
    update_query0 = sql.SQL("update sandbox.frequency "
                            "set freq = {} "
                            "where word = {}").format(
        sql.Literal(value),
        sql.Literal(word)
    )
    conn.execute(update_query0)
    conn.commit()









#preprocessed_w = preprocess_w(text, stop_words, punctuation_marks, morph)
# for word in preprocessed_w:
#     if preprocessed_w.count(word) < 3:
#         preprocessed_w.remove(word)


# preprocessed_p = []
# # preprocessed_text = preprocess_p(text, stop_words, punctuation_marks, morph)
# # finder = BigramCollocationFinder.from_words(preprocessed_text)
# #
# # phrases = finder.nbest(BigramAssocMeasures.likelihood_ratio, 20)
# # ngram_freq = finder.ngram_fd
# for bigram in phrases:
#     total_phrase = bigram[0] + ' ' + bigram[1]
#     frequency = ngram_freq[bigram]
#     for i in range(frequency):
#         preprocessed_p.append(total_phrase)
#print(preprocessed_w + preprocessed_p)