from spellchecker import SpellChecker
import language_tool_python
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
    return regrex_pattern.sub(r'',text)

def check_errors(text1):
    text = deEmojify(text1)
    if re.fullmatch(r'(\w){0,1}(\W){0,}', text):
        return text1, text1
    tool = language_tool_python.LanguageTool('ru-RU')

    spell = SpellChecker(language='ru')


    custom_dictionary_file = "vocab.txt"
    with open(custom_dictionary_file, "r", encoding="utf-8") as file:
        custom_dictionary = set(
            word.strip() for word in file.readlines() if word.strip())

    spell.word_frequency.load_words(custom_dictionary)

    ignored_words = set()
    for word in text.split():
        if any(c.isdigit() for c in word):
            ignored_words.add(word.lower())

    lowercased_text = ' '.join(word.lower() if not word[0].isupper() else word for word in text.split())

    words = [word for word in lowercased_text.split() if word.lower() not in ignored_words]
    nonexistent_words_copy = spell.unknown(words)
    grammar_errors = tool.check(lowercased_text)

    text = re.sub(r'(?<=\w)([^\w\s]+)', ' ', text)

    words = [word for word in text.split() if word.lower() not in ignored_words]
    nonexistent_words_copy = spell.unknown(words)
    grammar_errors = tool.check(text)
    nonexistent_words = []
    filtered_grammar_errors = []
    for error in grammar_errors:
        if not error.replacements: #or (len(str(error.replacements[0]).replace(str(error), '')) >2 or len(str(error).replace(str(error.replacements[0]), ''))>2):
            continue
        filtered_grammar_errors.append(error)


    for word in nonexistent_words_copy:
        if spell.candidates(word):
            continue
        nonexistent_words.append(word)

    text = text1

    return nonexistent_words, filtered_grammar_errors

def main():
    text = input("Введите текст для проверки: ")

    nonexistent_words, grammar_errors = check_errors(text)

    print("Несуществующие слова:")
    for word in nonexistent_words:
        print(word)

    print("\nГрамматические ошибки:")
    for error in grammar_errors:
        print(error)


main()


