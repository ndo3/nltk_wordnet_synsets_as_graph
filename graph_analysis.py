import json
import matplotlib.pyplot as plt
import numpy as np

with open("adj_to_num_associated_senses.json", "r") as lemmas, open("number_of_synsets_threedegs.json", "r") as synsets, open("number_of_antonyms.json", "r") as antonyms:
    # Woo
    lemmas_loaded, synsets_loaded, antonyms_loaded = json.load(lemmas), json.load(synsets), json.load(antonyms)
    print(lemmas_loaded['bad'] + synsets_loaded['bad'])
    # And then sort thing and start plotting
    lemmas_plus_synsets_loaded = {k: lemmas_loaded[k] + synsets_loaded[k] for k in lemmas_loaded}
    sorted_synsets = sorted(synsets_loaded.items(), key=lambda kv: -kv[1])
    sorted_lemmas = sorted(lemmas_loaded.items(), key=lambda kv: -kv[1])
    sorted_plus = sorted(lemmas_plus_synsets_loaded.items(), key=lambda kv: -kv[1])
    index = 0
    words, lemmas_count, synsets_count, antonyms_count = range(len(lemmas_loaded)), [], [], []
    words_that_are_different, difference = [], []
    for word, count in sorted_plus:
        if index > 500:
            break
        # words.append(word)
        lemmas_count.append(lemmas_loaded[word])
        synsets_count.append(synsets_loaded[word])
        if lemmas_loaded[word] != synsets_loaded[word]:
            words_that_are_different.append(word)
            difference.append(synsets_loaded[word] + lemmas_loaded[word])
        #antonyms_count.append(antonyms_loaded[word])
        index += 1
    words = range(len(lemmas_count))
    sorted_index = np.argsort(difference, axis=-1)
    # print(lemmas_count[300:500])
    words_that_are_different = [words_that_are_different[i] for i in sorted_index]
    difference = [difference[i] for i in sorted_index]
    # print(words_that_are_different[sorted_index])
    print(words_that_are_different)
    print(difference)
    plt.plot(words, lemmas_count)
    plt.plot(words, synsets_count)
    #plt.plot(words, antonyms_count)
    plt.legend(['original senses','synsets'])
    print('yo boy got here')
    plt.show()