import re

#основная функция
def detect_language(text):
    cleaned_text = re.sub(r'[^a-zA-Zа-яА-Яa-zA-Z]', ' ', text)
    english_letters = len(re.findall(r'[a-zA-Z]', cleaned_text))
    if english_letters > cleaned_text.count('')/2:
        return('english')
    else:
        return('russian')


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

conn = DB()

#изменить названия столбцов и таблицы на необходимые
query = """select 
* 
from (
select 
 "3_7" as words
from public.wyf_results wr
union all
select 
 "4_9"
from public.wyf_results wr
) t
where words is not null"""
conn.execute(query)
data = conn.fetch_all()

for row in data:
    text = str(row[0])
    print(text)
    print(detect_language(text))

