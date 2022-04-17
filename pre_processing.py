import collections
import json
from hazm import *
from parsivar import Normalizer, Tokenizer
from stop_words_finder import list_stop_words

inverted_index = {}
occurrence_of_each_word = {}
occurrence_of_each_word_in_each_doc = {}


def normalize_data(data):
    return Normalizer().normalize(data)


def pruning(data):
    pruned_letter = ['.', ':', ';', '!', '@', '#', '$', '%', '^', '&', '*',
                     '(', ')', '_', '-', '+', '=', ',', '1', '2', '3', '4',
                     '5', '6', '7', '8', '9', '0', '۱', '۲', '۳', '۴', '۵',
                     '۶', '۷', '۸', '۹', '۰', 'http', '\"', '/', '|', '÷',
                     '`', '~', '\u200c', '\u202b', '\u200f', 'https', '...',
                     '\xa0', '،', '(', ')'
                     ]
    for word in data:
        if word in pruned_letter:
            data.remove(word)
    return data


def del_stop_words(data):
    stop_words = list_stop_words()
    for stop_word in stop_words:
        for word in data:
            if stop_word == word:
                data.remove(word)
    return data


def find_steam(data):
    for i in range(0, len(data)):
        data[i] = Lemmatizer().lemmatize(data[i])
    return data


def tokenize_data(data):
    tokenizer = Tokenizer()
    return tokenizer.tokenize_words(data)


def create_index(content, doc_id):
    global inverted_index
    global occurrence_of_each_word
    for i in range(0, len(content)):
        if content[i] not in inverted_index.keys():
            inverted_index[content[i]] = [doc_id]
            occurrence_of_each_word[content[i]] = 1
        elif doc_id not in inverted_index[content[i]]:
            inverted_index[content[i]] += [doc_id]
            occurrence_of_each_word[content[i]] += 1
    return inverted_index


def write_inverted_index():
    file = open('inverted_index', 'w+')
    file.write(str(inverted_index))


def create_occurrence_of_each_word_in_each_doc(content, doc_id):
    global occurrence_of_each_word_in_each_doc
    occurrence_of_each_word_in_each_doc[doc_id] = {}
    for item in content:
        if item not in occurrence_of_each_word_in_each_doc[doc_id]:
            occurrence_of_each_word_in_each_doc[doc_id][item] = 1
        else:
            occurrence_of_each_word_in_each_doc[doc_id][item] += 1
    return occurrence_of_each_word_in_each_doc


def pre_processing(number_of_data):
    database = open('IR_data_news_12k.json', 'r').readline()
    data = json.loads(database)

    for i in range(150, number_of_data + 1):
        content = normalize_data(data[str(i)]['content'])
        content = tokenize_data(content)
        content = pruning(content)
        content = del_stop_words(content)
        content = find_steam(content)
        create_index(content, i)
        create_occurrence_of_each_word_in_each_doc(content, i)
        id = i
        url = data[str(i)]['url']
        title = data[str(i)]['title']
        payload = {
            "id": id,
            "url": url,
            "title": title,
            "content": content
        }
        name = str("docs/") + str(i) + ".json"
        file = open(name, 'w+')
        payload = json.dumps(payload)
        file.write(payload)

    write_inverted_index()


def search(query, database):
    global inverted_index
    doc_id_list = []
    not_list = []
    mines_list = []
    if database:
        data = open('inverted_index', 'r').readline()
        inverted_index = json.loads(open('inverted_index', 'r').readline().replace("\'", "\""))

    for i in range(0, len(query)):
        if query[i] == '!':
            not_list.append(query[i + 1])
        if query[i] in inverted_index.keys() and query[i] not in not_list:
            doc_id_list += inverted_index[query[i]]

    for item in not_list:
        if item in inverted_index.keys():
            mines_list += inverted_index[item]
    doc_id_list = [x for x in doc_id_list if x not in mines_list]
    occurrences = collections.Counter(doc_id_list)
    return occurrences.most_common()


def main():
    # pre_processing(200)
    print(inverted_index)
    print("database search 1  dynamic search 2 : ")
    query = input()
    query = normalize_data(query)
    query = query.split()
    print(search(query, True))


if __name__ == '__main__':
    main()
