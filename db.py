import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")


#далее изменить на необходимые параметры подключения к бд
class DB:
    def __init__(self):
        self.conn = (psycopg2.connect(
            host= db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            dbname=db_name,
            sslmode='require'
        ))
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
