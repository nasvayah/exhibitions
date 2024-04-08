import rake_nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from OSRus import data2, conn
import re

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

punctuation_marks = ['!', ',', '(', ')', ':', '-', '?', '.', '..',
                     '...', '«', '»', ';', '–', '--', '<', '>', '=', '+', '\'', '!!', '!!!']
stop_words = stopwords.words("russian") + ['всё', 'это'] + punctuation_marks
r = rake_nltk.Rake(stop_words)

all_ranked= []
all_insert_queries = []
for row in data2:
    id = row[0]
    question_name = row[1]
    date_create = str(row[2])
    txt = deEmojify(str(row[3]))
    for i in txt:
        if i in punctuation_marks:
            txt.replace(i, ' ')
    txt.replace("'", ' ')
    r = rake_nltk.Rake(stop_words)
    r.extract_keywords_from_text(txt)
    ranked = r.get_ranked_phrases_with_scores()
    unique_phrases = set()
    for score, phrase in ranked:
        if len(word_tokenize(phrase.lower())) > 1 and score != 1.0:
            unique_phrases.add(phrase)
    for phrase in unique_phrases:
        update_query = f"""
                insert into sandbox.phrases(id, question_name, date_create, phrase)
                values({id},'{question_name}','{date_create}','{phrase}');
                update sandbox.phrases_old_id
                set max_id={id}
                where id = 1
        """
        all_insert_queries.append(update_query)
    #all_ranked = all_ranked + ranked
    print(ranked)
for query in all_insert_queries:
    conn.execute(query)
    conn.commit()
