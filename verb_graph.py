# Made by ndo3.github.io (ndo3@cs.brown.edu)

# first import wordnet
from nltk.corpus import wordnet as wn
from all_graph import *
import json
from collections import defaultdict

class InvalidInputException(Exception):
    def __str__(self):
        return "Invalid Input Given."

class InvalidGraphException(Exception):
    def __str__(self):
        return "Ruh Roh. Something is bad. Contact Nam at ndo3@cs.brown.edu."


# for synset in list(wn.all_synsets('v')):
#     all_lemmas, all_antonyms = synset.lemmas(), []
#     for lemma in all_lemmas:
#         if len(lemma.antonyms()) != 0:
#             print(synset)
#     # [all_antonyms.append(a) for a ]
#     # if len(synset.antonyms()):
#     #     print(synset)
#     # print(synset)
#     # print()
    


################################################################################################
######## -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #########
######## -=-=-=-=-=-=-=-=-=-=-=-=-=-=-= VERB GRAPH PORTION =-=-=-=-=-=-=-=-=-=-=-=-=-= #########
######## -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #########
################################################################################################

# Each edge represent a kind of connection between two words
class CauseEdge:
    def __init__(self, node_one, node_two): # This is particularly not a symmetric relationship - word one causes word two and not the other way around
        self.node_one, self.node_two = node_one, node_two
        self.type_of_connection = 'causation'

class VerbNode:
    def __init__(self, id, word):
        # maybe for housekeeping - we might need an ID later; Instantiating given the word and lemma and word_type
        self.id, self.word = id, word
        # Keep track of the things that are related to the node
        self.list_of_synsets = wn.synsets(word, pos=wn.VERB)
        self.list_of_lemmas = []
        # Instantiating the list of edges and stuff
        self.list_of_edges, self.list_of_synset_edges, self.list_of_antonym_edges = [], [], []
        # Instantiate even more list of edges
        self.list_of_causation_edges, self.list_of_hypernym_edges, self.list_of_hyponym_edges = [], [], []
        # The dictionary that is id (of node that we are connected to) -> [synsets that they are connected by]
        self.connections, self.connections_edges, self.antonymous_node_ids = {}, {}, []

class VerbGraph:
    def __init__(self):
        self.node_dictionary = NodeDictionary()
        self.all_words = from_synsets_to_words(wn.all_synsets('v'))

    def load_graph(self):
        # Get the list of all synsets of verbs
        all_words = from_synsets_to_words(wn.all_synsets('v'))
        # For each word
        for id, word in enumerate(all_words):
            new_node = VerbNode(id, word) # First create a node
            # Then update the NodeDictionary
            assert word not in self.node_dictionary.word_to_id and word not in self.node_dictionary.word_to_node
            self.node_dictionary.word_to_id[word] = id
            self.node_dictionary.word_to_node[word] = new_node
            self.node_dictionary.id_to_node[id] = word
            self.node_dictionary.list_of_all_nodes.append(new_node)
            self.node_dictionary.word_to_num_synsets[word] = len(new_node.list_of_synsets)

    def load_nodes(self):
        pass

    def load_synset_edges(self):
        pass

    def load_antonym_edges(self):
        pass

    def load_causation_edges(self):
        pass

    def load_hypernym_edges(self):
        pass

    def load_hyponym_edges(self):
        pass

################################################################################################
######## -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #########
######## -=-=-=-=-=-=-=-=-=-=-=-= PART OF ANALYSIS FOR GRAPH =-=-=-=-=-=-=-=-=-=-=-=-= #########
######## -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #########
################################################################################################