from spellchecker import SpellChecker
import re
from OSRus import conn


def deEmojify(text):
    regrex_pattern = re.compile(pattern = "["
                                u"\U00000000-\U00000009"
                                u"\U0000000B-\U0000001F"
                                u"\U00000080-\U00000400"
                                u"\U00000402-\U0000040F"
                                u"\U00000450-\U00000450"
                                u"\U00000452-\U0010FFFF"
                                "]+", flags = re.UNICODE)
    return regrex_pattern.sub(r' ээ ',text)

def check_errors(text1):
    text = deEmojify(text1)
    if re.fullmatch(r'(\W){0,}', text):
        return True



    ignored_words = set()
    for word in text.split():
        if any(c.isdigit() for c in word):
            ignored_words.add(word.lower())

    lowercased_text = ' '.join(word.lower() if not word[0].isupper() else word for word in text.split())

    words = [word for word in lowercased_text.split() if word.lower() not in ignored_words]

    text = re.sub(r'([^\w\s]|\_)+', ' ', text)
    text = re.sub(r'(\w)\1{2,}', r'\1\1', text)
    text = re.sub(r'[a-zA-Z]', '', text)

    words = [word for word in text.split() if word.lower() not in ignored_words]

    nonexistent_words = [word for word in words if not spell.correction(word)]

    text1 = text

    return nonexistent_words

def result(text, custom_dictionary):

    nonexistent_words= check_errors(text)

    if nonexistent_words:
        return True
    return False



#изменить названия столбцов и таблицы на необходимые
query0 = """select 
max_id from public.old_id"""
conn.execute(query0)
data0 = conn.fetch_all()
for row in data0:
    max_id = data0[0]
    print(int(str(max_id)[1:-2]))
    max_id = int(str(max_id)[1:-2])



#изменить названия столбцов и таблицы на необходимые
query = f"""select
guides.id, guides.question_name, guides.question_id, guides.question_answer
from public.guides
where question_name in (
    'answer_short_text_37961013',
    'answer_short_text_39100929',
    'answer_long_text_37961085',
    'answer_short_text_39100908',
    'answer_long_text_37961122'
    )
AND guides.question_answer notnull and guides.question_answer!='' and guides.question_answer!=' ' and guides.id>= {max_id}
;"""
conn.execute(query)
data = conn.fetch_all()


#изменить названия столбцов и таблицы на необходимые
query1 = """select guides_info.fio from guides_info"""
conn.execute(query1)
names = conn.fetch_all()
splnames = []
for i in names:
    name = str(i[0]).lower()
    splnames = splnames + name.split()
spell = SpellChecker(language='ru')

custom_dictionary_file = "vocab.txt"
with open(custom_dictionary_file, "r", encoding="utf-8") as file:
    custom_dictionary = set(
        word.strip() for word in file.readlines() if word.strip())


custom_dictionary = custom_dictionary.union(set(splnames))
spell.word_frequency.load_words(custom_dictionary)

id_file = open("id_file.txt","w")
question_id_file = open("question_id_file.txt", "w")
for row in data:
    id = row[0]
    question_name = row[1]
    question_id = row[2]
    text = row[3]
    if result(text, custom_dictionary):
        print(id, ' ',question_id, ' ', text)
        id_file.write("'" + str(id) +"'" + ','+ '\n')
        question_id_file.write("'" + str(question_id)+ "'"+ ',' + '\n')
        # изменить названия столбцов и таблицы на необходимые
        update_query = f""" update public.guides
        set question_answer = ''
        where question_name in (
            'answer_short_text_37961013',
            'answer_short_text_39100929',
            'answer_long_text_37961085',
            'answer_short_text_39100908',
            'answer_long_text_37961122'
            )
        AND guides.question_answer notnull and guides.question_answer!='' and guides.question_answer!=' '
        AND guides.id = {id} AND guides.question_id = {question_id}
        ;
        insert into public.deleted_guides(id, question_name, question_id, question_answer)
        values({id},'{question_name}',{question_id},'{text}');
        update public.old_id 
        set max_id={id}
        where id = 1
        ;"""
        conn.execute(update_query)
        conn.commit()
        




conn.close()

