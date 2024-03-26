import re
import pandas as pd
import os.path
import psycopg2
from dotenv import load_dotenv


load_dotenv()

#далее изменить на необходимые параметры подключения к бд
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

# conn = DB()
# query = """select
# guides.question_answer
# from public.guides
# where question_name in (
#     'answer_short_text_37961013',
#     'answer_short_text_39100929',
#     'answer_long_text_37961085',
#     'answer_short_text_39100908',
#     'answer_long_text_37961122'
#     )
# AND guides.question_answer notnull and guides.question_answer!='' and guides.question_answer!=' '
# """
# conn.execute(query)
# data = conn.fetch_all()

conn = DB()
query = """select 
* 
from (
select 
 "3_7" as words
from public.wyf_results wr

) t
where words is not null
"""
conn.execute(query)
data = conn.fetch_all()

text = ''
# data = pd.read_csv('ВФМ_гиды_комментарии.csv', sep='/n', index_col='id');
for row in data:
    txt = str(row[0])
    text = text + ' ' + txt


text = re.sub(r'==.*?==+', '', text) # удаляем лишние символы
text = text.replace('\n', '') # удаляем знаки разделения на абзацы

import matplotlib.pyplot as plt

import nltk
from nltk.corpus import stopwords

def plot_cloud(wordcloud):
    plt.figure(figsize=(40, 30))
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.tight_layout()

from wordcloud import WordCloud, ImageColorGenerator


STOPWORDS_RU = stopwords.words("russian")

wordcloud = WordCloud(width = 2000,
                      height = 1500,
                      random_state=1,
                      background_color='black',
                      margin=20,
                      colormap='Pastel1',
                      collocations=False,
                      stopwords = STOPWORDS_RU).generate(text)

plot_cloud(wordcloud)
plt.show()