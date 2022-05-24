import json
import math
from scipy import spatial
from hazm import *
from parsivar import Normalizer, Tokenizer, FindStems
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
        steamer = FindStems()
        data[i] = steamer.convert_to_stem(data[i])
    return data


def tokenize_data(data):
    tokenizer = Tokenizer()
    return tokenizer.tokenize_words(data)


def check_nonsense(word):
    if ',' not in word and '/' not in word and '-' not in word and \
            '=' not in word and '_' not in word and '!' not in word and '@' not in word and ':' not in word \
            and ';' not in word and '٪' not in word and '^' not in word and '&' not in word \
            and '*' not in word and '(' not in word and '(' not in word and ')' not in word and '(' not in word \
            and '[' not in word and ']' not in word and '}' not in word and '{' not in word:
        if word.startswith('\'') and word.endswith('\''):
            return True
    return False


def create_index(content, doc_id):
    global inverted_index
    global occurrence_of_each_word

    for i in range(0, len(content)):
        if not check_nonsense(content[i]):
            if content[i] not in inverted_index.keys():
                inverted_index[content[i]] = [[doc_id]]
                occurrence_of_each_word[content[i]] = 1
            elif [doc_id] not in inverted_index[content[i]]:
                inverted_index[content[i]] += [[doc_id]]
                occurrence_of_each_word[content[i]] += 1
        filename = 'occurrence_of_each_word-' + str(doc_id)
        file = open('files/occurrence_of_each_word', 'w+')
        file.write(str(occurrence_of_each_word))

    return inverted_index


def cal_tf(occurrence_of_word_in_doc):
    return 1 + math.log(occurrence_of_word_in_doc, 10)


def cal_idf(word, N, inverted_index):
    nt = len(inverted_index[word])
    return math.log(N / nt, 10)


def cal_tfidf(inverted_index):
    for key, value in inverted_index.items():
        for doc_id in value:
            data = json.loads(open('files/by_id/' + str(doc_id[0]), 'r').readline().replace("\'", "\""))
            freq = data[key]
            tfidf = cal_tf(freq) * cal_idf(key, int(len(inverted_index)), inverted_index)
            doc_id.append(tfidf)
    return inverted_index


def write_inverted_index():
    global inverted_index
    file = open('inverted_index', 'w')
    inverted_index = cal_tfidf(inverted_index)
    file.write(str(inverted_index))


def create_occurrence_of_each_word_in_each_doc(content, doc_id):
    global occurrence_of_each_word_in_each_doc
    occurrence_of_each_word_in_each_doc = {}
    for item in content:
        if item not in occurrence_of_each_word_in_each_doc:
            occurrence_of_each_word_in_each_doc[item] = 1
        else:
            occurrence_of_each_word_in_each_doc[item] += 1
    file = open('files/by_id/' + str(doc_id), 'w+')
    file.write(str(occurrence_of_each_word_in_each_doc))
    return occurrence_of_each_word_in_each_doc


def pre_processing(number_of_data):
    database = open('IR_data_news_12k.json', 'r').readline()
    data = json.loads(database)

    for i in range(0, number_of_data):
        print(i)
        content = normalize_data(data[str(i)]['content'])
        content = tokenize_data(content)
        content = pruning(content)
        content = del_stop_words(content)
        content = find_steam(content)
        create_occurrence_of_each_word_in_each_doc(content, i)
        create_index(content, i)
        # save single file
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


def cal_tfidf_for_query(query, inverted_index):
    for item in query:
        if item == '-':
            query.remove(item)

    q_dic = {}
    vector = []
    for item in query:
        if item not in q_dic:
            q_dic.update({item: 1})
        else:
            q_dic[item] += 1
    for key, value in q_dic.items():
        if key in inverted_index.keys():
            tfidf = cal_tf(value) * cal_idf(key, int(len(inverted_index)), inverted_index)
            vector.append(tfidf)
        else:
            vector.append(0)
    return vector


def search(query, database):
    global inverted_index
    doc_id_list = []
    not_list = []
    mines_list = []
    phrase_list = []
    dic = {}

    if database:
        inverted_index = json.loads(open('inverted_index', 'r').readline().replace("\'", "\""))
        create_champion_list_once(inverted_index)
    champion_list = get_champion_dic()

    # check phrase
    started = False
    for i in range(0, len(query)):
        if query[i] == '-' and not started:
            started = True
        elif query[i] == '-' and started:
            started = False
        if started and query[i] != '-':
            phrase_list.append(query[i])

    # check not and
    for i in range(0, len(query)):
        if query[i] == '!':
            not_list.append(query[i + 1])
        if query[i] in champion_list.keys() and query[i] not in not_list:
            for item in champion_list[query[i]]:
                doc_id_list += [item]
                if item[0] not in dic.keys():
                    vector_list = [0 for i in query]
                    dic.update({item[0]: vector_list})
                    dic[item[0]][i] = item[1]
                elif item[0] in dic.keys():
                    dic[item[0]][i] = item[1]
    # delete not words
    for item in not_list:
        if item in champion_list.keys():
            mines_list += champion_list[item]

    doc_id_list = [x for x in doc_id_list if x not in mines_list]

    for item in doc_id_list:
        if phrase_list:
            filename = "docs/" + str(item[0]) + ".json"
            database = open(filename, 'r').readline()
            data = json.loads(database)
            content = data["content"]

            if phrase_list[0] not in content and phrase_list[1] not in content:
                doc_id_list.remove(item)
            elif phrase_list[0] in content and phrase_list[1] in content \
                    and abs(content.index(phrase_list[0]) - content.index(phrase_list[1])) != 1:
                doc_id_list.remove(item)

    output_dic = {key: dic[key] for key in dic.keys() if key in [item[0] for item in doc_id_list]}
    return output_dic


def cal_similarity(query_vector, doc_vector):
    return 1 - spatial.distance.cosine(query_vector, doc_vector)


def cal_similarity_for_docs(dic, query_vector):
    output_similarity = {}
    for key, value in dic.items():
        output_similarity.update({key: cal_similarity(query_vector, value)})
    return output_similarity


def get_result(dic, query_vector):
    output_similarity = cal_similarity_for_docs(dic, query_vector)
    output_similarity = dict(sorted(output_similarity.items(), key=lambda x: x[1], reverse=True))
    for key, value in output_similarity.items():
        doc_id = key
        filename = 'docs/' + str(doc_id) + '.json'
        file = open(filename)
        content = file.readline()
        print("doc_id: " + str(doc_id))
        print("title: " + str(json.loads(content)["title"]))
        print("url: " + str(json.loads(content)["url"]))


def create_champion_list_once(inverted_index):
    champion_dic = {}
    for key, value in inverted_index.items():
        value = sorted(value, key=lambda x: -x[1])
        champion_dic.update({key: value})
    file = open('champion_list', 'w+')
    file.write(str(champion_dic))


def get_champion_dic():
    return json.loads(open('champion_list', 'r').readline().replace("\'", "\""))


def get_inverted_index():
    return json.loads(open('inverted_index', 'r').readline().replace("\'", "\""))


def main():
    while True:
        print("Enter process mode (1) or database mode (2) write champion list (3):")
        mode = input()
        if mode == '2':
            print("Enter query: ")
            query = input()
            query = normalize_data(query)
            query = query.split()
            dic = search(query, True)
            get_result(dic, cal_tfidf_for_query(query, get_inverted_index()))
        elif mode == '1':
            print("Enter number of docs to process:")
            number = input()
            print("wait please, its processing...")
            pre_processing(int(number))
            print("Enter query: ")
            query = input()
            query = normalize_data(query)
            query = query.split()
            dic = search(query, False)
            get_result(dic, cal_tfidf_for_query(query, get_inverted_index()))
        elif mode == '3':
            print("wanna recreate inverted_index (y or n): ")
            ans = input()
            if ans == 'n':
                create_champion_list_once(inverted_index)
            if ans == 'y':
                print("Enter size:")
                size = input()
                pre_processing(int(size))
                create_champion_list_once(get_inverted_index())


if __name__ == '__main__':
    main()
