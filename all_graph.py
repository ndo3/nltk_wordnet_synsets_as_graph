# first import wordnet
from nltk.corpus import wordnet as wn
import json
from collections import defaultdict

################################################################################################
####### -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- ##########
####### -=-=-=-=-=-=-=-=-=-=-=-=-= HELPER FUNCTIONS PORTION =-=-=-=-=-=-=-=-=-=-=-=-= ##########
####### -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- ##########
################################################################################################

def from_synsets_to_words(list_of_synsets):
    list_of_words = []
    for synset in list_of_synsets:
        lemmas = synset.lemmas()
        for lemma in lemmas:
            if lemma.name() not in list_of_words: list_of_words.append(lemma.name())
    return list_of_words

def from_synsets_to_lemmas(list_of_synsets):
    list_of_lemmas = []
    for synset in list_of_synsets:
        lemmas = synset.lemmas()
        for lemma in lemmas:
            if lemma not in list_of_lemmas: list_of_lemmas.append(lemma)
    return list_of_lemmas


def from_words_to_synsets(list_of_words, what_type=wn.ADJ):
    list_of_synsets = []
    for word in list_of_words:
        new_synsets = wn.synsets(word, pos=what_type)
        for synset in new_synsets:
            # Appending synset
            if synset not in list_of_synsets: list_of_synsets.append(synset)
    return list_of_synsets

def from_synset_to_list_of_words(synset):
    lemmas = synset.lemmas()
    return [lemma.name() for lemma in lemmas]

def add_key_value_to_dictionary_that_is_of_type_key_to_a_list(key, value, the_dictionary):
    if key in the_dictionary: the_dictionary[key].append(value)
    else: the_dictionary[key] = [value]

def get_senses_of_a_word_based_on_a_list_of_synsets(word, list_of_synsets):
    all_lemmas = []
    for synset in list_of_synsets:
        all_lemmas.extend(synset.lemmas())
    # list_of_lemmas = from_synsets_to_lemmas(list_of_synsets)
    return [lemma for lemma in all_lemmas if lemma.name() == word]

# Classes that are useable by pretty much all graphs

class SynsetEdge:
    def __init__(self, node_one, node_two, synset):
        # Storing the important information
        self.node_one, self.node_two, self.synset, self.type_of_connection = node_one, node_two, synset, 'synonymy'

class AntonymEdge:
    def __init__(self, node_one, node_two):
        self.node_one, self.node_two, self.type_of_connection = node_one, node_two, 'antonymy'

class NodeDictionary:
    def __init__(self, what_type=wn.ADJ):
        self.list_of_all_nodes, self.id_to_node, self.id_to_word = [], {}, {} # extraly added, need to evaluate necessity
        # cuz there is no way to hash a Node
        self.word_to_id, self.word_to_node, self.word_to_num_synsets, self.word_to_num_antonyms = {}, {}, {}, {}






#### THIS CODE WAS ONCE USED TO WRITE THE STUFF TO ADJ_TO_NUM_ASSOCIATED_LEMMAS
def adj_to_num_associated_lemmas():
    og_dict = {}
    all_adjectives = from_synsets_to_words(wn.all_synsets('a'))
    for adj in all_adjectives:
        og_dict[adj] = len(get_senses_of_a_word_based_on_a_list_of_synsets(adj, wn.synsets(adj, pos=wn.ADJ)))
        if adj == 'bad':
            print(og_dict)
        # if len(get_senses_of_a_word_based_on_a_list_of_synsets(adj, wn.synsets(adj, pos=wn.ADJ))) > 1 :
        #     print(adj)
        # if adj == 'bad':
        #     print(from_synsets_to_lemmas(wn.synsets(adj, pos=wn.ADJ)))
        
    with open("adj_to_num_associated_senses.json", "w") as to_write_file:
        json.dump(og_dict, to_write_file)

    # print(sorted(og_dict.items(), key=lambda kv: kv[1]))