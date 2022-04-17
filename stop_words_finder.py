def list_stop_words():
    word_list = []
    with open('stop_words.txt', 'r') as file:
        for line in file:
            word = line.strip()
            word_list.append(word)
    # word_list = list(set(word_list))
    return word_list

