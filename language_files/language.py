import re
from db import conn

#основная функция
def detect_language(text):
    cleaned_text = re.sub(r'[^a-zA-Zа-яА-Яa-zA-Z]', ' ', text)
    english_letters = len(re.findall(r'[a-zA-Z]', cleaned_text))
    if english_letters > cleaned_text.count('')/2:
        return('english')
    else:
        return('russian')



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

