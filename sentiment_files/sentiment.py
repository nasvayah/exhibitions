from transformers import BertForSequenceClassification, BertTokenizer
import torch

model = BertForSequenceClassification.from_pretrained('./fine_tuned_model')
tokenizer = BertTokenizer.from_pretrained('blanchefort/rubert-base-cased-sentiment')

def predict_sentiment(text):
    encoded_input = tokenizer(text, padding='max_length', truncation=True, max_length=128, return_tensors='pt')
    with torch.no_grad():
        output = model(**encoded_input)
    logits = output.logits
    probabilities = torch.softmax(logits, dim=1)
    predicted_class = torch.argmax(probabilities, dim=1).item()
    res = ''
    if predicted_class == 2 :
        res = 'POSITIVE'
    elif predicted_class == 1:
        res = 'NEUTRAL'
    elif predicted_class == 0 :
        res = 'NEGATIVE'
    return res


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
cp 
conn = DB()
query = """select
res0.question_answer
from sandbox.res0
where question_name in (

    'answer_long_text_37961122'
    )
AND res0.question_answer notnull and res0.question_answer!='' and res0.question_answer!=' '
;"""
conn.execute(query)
data = conn.fetch_all()

i = 0
neu = 0
pos = 0
neg= 0
for row in data:
    text = str(row[0])
    i+=1
    print(i)
    res = predict_sentiment(text)
    print(text)
    print (res)
    if "NEUTRAL" == res:
        neu+=1
        update_query = f""" update sandbox.res0
        set new_score = 'NEUTRAL'
        where question_answer = '{text}'
        """
    elif "POSITIVE" == res:
        pos+=1
        update_query = f""" update sandbox.res0
        set new_score = 'POSITIVE'
        where question_answer = '{text}'
        """
    elif "NEGATIVE" == res:
        neg+=1
        update_query = f""" update sandbox.res0
        set new_score = 'NEGATIVE'
        where question_answer = '{text}'
        """
    conn.execute(update_query)
    conn.commit()
print('Number of anwsers: ', i)
print('Positive: ', pos)
print('Negative: ', neg)
print('Neutral: ', neu)


