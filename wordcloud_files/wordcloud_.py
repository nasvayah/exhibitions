import re

from db import conn


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