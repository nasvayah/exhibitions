import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_name = os.getenv('DB_NAME')


#далее изменить на необходимые параметры подключения к бд
class DB:
    def __init__(self):
        self.conn = psycopg2.connect(
            host= db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            dbname=db_name,
            sslmode='require'
        )
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

query0 = """select 
max_id from sandbox.freq_old_id"""
conn.execute(query0)
data0 = conn.fetch_all()
for row in data0:
    max_id = data0[0]
    #print(int(str(max_id)[1:-2]))
    max_id = int(str(max_id)[1:-2])

#изменить названия столбцов и таблицы на необходимые
query = f"""select
guides.id, guides.question_name, guides.date_create, guides.question_answer
from public.guides
where question_name in (
    'answer_long_text_37961085',
    'answer_long_text_37961122'
    )
AND guides.question_answer notnull and guides.question_answer!='' and guides.question_answer!=' ' and guides.id> {max_id}
order by id asc
;"""
conn.execute(query)
data = conn.fetch_all()

query1 = """select
guides.id, guides.question_name, guides.question_id, guides.question_answer
from public.guides
where question_name in (
    'answer_short_text_37961013',
    'answer_short_text_39100929',
    'answer_long_text_37961085',
    'answer_short_text_39100908',
    'answer_long_text_37961122'
    )
AND guides.question_answer notnull and guides.question_answer!='' and guides.question_answer!=' '
order by id asc
;"""
conn.execute(query1)
data1 = conn.fetch_all()


query3 = """select 
max_id from sandbox.phrases_old_id"""
conn.execute(query3)
data3 = conn.fetch_all()
for row in data3:
    max_id1 = data3[0]
    #print(int(str(max_id)[1:-2]))
    max_id1 = int(str(max_id1)[1:-2])

query2 = f"""select
guides.id, guides.question_name, guides.date_create, guides.question_answer
from public.guides
where question_name in (
    'answer_long_text_37961085',
    'answer_long_text_37961122'
    )
AND guides.question_answer notnull and guides.question_answer!='' and guides.question_answer!=' ' and date_create != '2024-03-22 04:37:28'
and guides.id> {max_id1}
order by id asc
;"""
conn.execute(query2)
data2 = conn.fetch_all()
