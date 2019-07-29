# Made by ndo3.github.io (ndo3@cs.brown.edu)

# first import wordnet
from nltk.corpus import wordnet as wn

class InvalidInputException(Exception):
    def __str__(self):
        return "Invalid Input Given."

class InvalidGraphException(Exception):
    def __str__(self):
        return "Ruh Roh. Something is bad. Contact Nam at ndo3@cs.brown.edu."

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
            if lemma.name() not in list_of_words:
                list_of_words.append(lemma.name())
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
            if synset not in list_of_synsets:
                list_of_synsets.append(synset)
    return list_of_synsets

def from_synset_to_list_of_words(synset):
    lemmas = synset.lemmas()
    return [lemma.name() for lemma in lemmas]

def add_key_value_to_dictionary_that_is_of_type_key_to_a_list(key, value, the_dictionary):
    if key in the_dictionary:
        the_dictionary[key].append(value)
    else:
        the_dictionary[key] = [value]


################################################################################################
######## -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #########
######## -=-=-=-=-=-=-=-=-=-=-=-=-= ADJECTIVE GRAPH PORTION =-=-=-=-=-=-=-=-=-=-=-=-=- #########
######## -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #########
################################################################################################

class SynsetEdge:
    def __init__(self, node_one, node_two, synset):
        # Storing the important information
        self.node_one = node_one
        self.node_two = node_two
        self.synset = synset
        # and then just storing type_of_connection so that it's easily accessible
        self.type_of_connection = 'synonymy'
        
class AntonymEdge:
    def __init__(self, node_one, node_two):
        self.node_one = node_one
        self.node_two = node_two
        self.type_of_connection = 'antonymy'
        

class AdjectiveNode:
    def __init__(self, id, word):
        # maybe for housekeeping - we might need an ID later
        self.id = id
        # Instantiating given the word and lemma and word_type
        self.word = word
        # There is a list of synsets which are associated with that word, which
        # will say that we will also need a list of edges that are connected to
        # the node because the types of synsets are only the nature of the edges
        # and not all the edges themselves
        self.list_of_synsets = wn.synsets(word, pos=wn.ADJ)
        # Lists to store the important informations
        self.list_of_edges = []
        self.list_of_synset_edges = []
        self.list_of_antonym_edges = []
        # By the way, Brooklyn Nine-Nine rocks
        # The dictionary that is id (of node that we are connected to) -> [synsets that they are connected by]
        self.connections = {} # This connections is specifically for synsets connections
        self.connections_edges = {} # This connections_edges is specifically for edges
        self.antonymous_node_ids = []


class NodeDictionary:
    def __init__(self, what_type=wn.ADJ):
        self.list_of_all_nodes = []
        self.id_to_node = {}
        self.id_to_word = {} # extraly added, need to evaluate necessity
        # cuz there is no way to hash a Node
        self.word_to_id = {}
        self.word_to_node = {}

class AdjectiveGraph:
    def __init__(self):
        self.node_dictionary = NodeDictionary()
        self.load_graph()
    
    ######################### THIS PART IN THE CLASS IS TO INSTANTIATE ALL THE VARIABLES PROPERLY #########################

    # You would make the graph that has each node be the word, and each edge
    # represent a synset
    def load_graph(self):
        # First, load all the nodes
        self.load_nodes()
        # Second, load all the synonym set edges
        self.load_synset_edges()
        # Third, load all the antonym set edges
        self.load_antonym_edges()
        
    # Function to load the words
    def load_nodes(self):
        # Get the list of all synsets
        all_words = from_synsets_to_words(wn.all_synsets('a'))
        # For each word
        for id, word in enumerate(all_words):
            # First create a node
            new_node = AdjectiveNode(id, word)
            # Then update the NodeDictionary
            assert word not in self.node_dictionary.word_to_id and word not in self.node_dictionary.word_to_node
            self.node_dictionary.word_to_id[word] = id
            self.node_dictionary.word_to_node[word] = new_node
            self.node_dictionary.id_to_node[id] = word
            self.node_dictionary.list_of_all_nodes.append(new_node)

    def load_synset_edges(self):
        ############# ----- BEGIN DEFINING HELPER FUNCTIONF FOR THIS FUNCTION ----- #############
        # This helper function is to help determine if two nodes are addable
        def addable(node_one, node_two, synset):
            # If there exists no edge between the two yet
            if node_two.id not in node_one.connections and node_one.id not in node_two.connections:
                return True
            # If there exists both ids in other's respective dictionaries (check this so that there is no error :P)
            elif node_two.id in node_one.connections and node_one.id in node_two.connections:
                if synset not in node_one.connections[node_two.id] and synset not in node_two.connections[node_one.id]:
                    return True
                # else if it is in both then we return false
                elif synset in node_one.connections[node_two.id] and synset in node_two.connections[node_one.id]:
                    return False
                else: raise InvalidGraphException('There exists asymmetry between adding synsets into the two nodes\' connections dictionary lists')
            else: 
                # print(node_two.id not in node_one.connections)
                # print(node_one.id not in node_two.connections)
                raise InvalidGraphException('There exists asymmetry between adding edges into the two nodes\' connections dictionary')
        # This helper function is to add edge between two nodes
        def add_edge(node_one, node_two, synset):
            # First, you would create a new edge
            new_edge = SynsetEdge(node_one, node_two, synset)
            # Second, you would make the nodes know about the edges that they be connected to
            node_one.list_of_edges.append(new_edge)
            node_one.list_of_synset_edges.append(new_edge)
            node_two.list_of_edges.append(new_edge)
            node_two.list_of_synset_edges.append(new_edge)
            # Third, you would make the nodes know that they are attached to each other (oh how romantic) by
            # their respective synsets
            # Updating node_one's connections dictionary and node_two's connections dictionary
            add_key_value_to_dictionary_that_is_of_type_key_to_a_list(node_two.id, synset, node_one.connections)
            add_key_value_to_dictionary_that_is_of_type_key_to_a_list(node_one.id, synset, node_two.connections)
            # Fourth, you would update node_one's connections_edges and node_two's connections_edges dictionary
            add_key_value_to_dictionary_that_is_of_type_key_to_a_list(node_two.id, new_edge, node_one.connections_edges)
            add_key_value_to_dictionary_that_is_of_type_key_to_a_list(node_one.id, new_edge, node_two.connections_edges)

        ############# ----- END OF DEFINING HELPER FUNCTIONS FOR THIS FUNCTION ----- #############

        # For each synset, you would then get the words associated with it, and then you
        # would make a new edge that would connect those nodes together
        for synset in wn.all_synsets('a'):
            # You would get associating words
            associating_words = from_synset_to_list_of_words(synset)
            # And the associating nodes from it
            associating_nodes = [self.node_dictionary.word_to_node[word] for word in associating_words]
            # For each pair of nodes
            for node_one in associating_nodes:
                for node_two in associating_nodes:
                    # If node_one is not equal to node_two, or the nodes are not connected ! by ! the ! same ! synset !
                    # we would add an edge between them
                    if node_one != node_two and addable(node_one, node_two, synset):
                        add_edge(node_one, node_two, synset)


    def load_antonym_edges(self):
        def addable(node_one, node_two):
            if node_two.id not in node_one.antonymous_node_ids and node_one.id not in node_two.antonymous_node_ids:
                return True
            elif node_two.id in node_one.antonymous_node_ids and node_one.id in node_two.antonymous_node_ids:
                return False
            else: # error checking
                raise InvalidGraphException('Something is messed up with keeping track of antonymous_node_ids')
        def add_edge(node_one, node_two):
            # First, you would create a new Antonymous Edge
            new_edge = AntonymEdge(node_one, node_two)
            # Second, you would add the edge to the respective housekeeping lists in node_one and node_two
            node_one.list_of_edges.append(new_edge)
            node_one.list_of_antonym_edges.append(new_edge)
            node_two.list_of_edges.append(new_edge)
            node_two.list_of_antonym_edges.append(new_edge)
            # Add to list to keep tracks of antonymous nodes
            node_one.antonymous_node_ids.append(node_two.id)
            node_two.antonymous_node_ids.append(node_one.id)
            # Third, you would add the edge to the connections_edges dictionaries in the respective nodes
            add_key_value_to_dictionary_that_is_of_type_key_to_a_list(node_two.id, new_edge, node_one.connections_edges)
            add_key_value_to_dictionary_that_is_of_type_key_to_a_list(node_one.id, new_edge, node_two.connections_edges)
        # Get all the lemmas out there
        list_of_lemmas = from_synsets_to_lemmas(wn.all_synsets('a'))
        # For each lemma, load all the lemmas that are antonyms with the lemma
        for og_lemma in list_of_lemmas:
            # The original word of the lemma that we are dealing with
            og_word = og_lemma.name()
            # Get the node that we are dealing with
            og_node = self.node_dictionary.word_to_node[og_word]
            # list of antonymous lemmas: (oh yay efficiency)
            antonymous_words = [lemma.name() for lemma in og_lemma.antonyms()]
            antonymous_nodes = [self.node_dictionary.word_to_node[word] for word in antonymous_words]
            # Loop through each of the anonymous 
            for antonymous_node in antonymous_nodes:
                # Check if the og_node and each of the antonymous_node is (1) the same and (2) already connected by an AntonymyEdge
                if og_node == antonymous_node: raise InvalidGraphException('Uh this is actually funny. A word is antonymous to itself. Tell Nam - he might not be able to fix it but he will definitely find it amusing.')
                if addable(og_node, antonymous_node): add_edge(og_node, antonymous_node)
    
    #######################################################################################################################
    
    #################### THIS PART IN THE CLASS IS TO ACCESS THE PROPERTIES AFTER PUTTING IT IN A GRAPH ###################
    def get_opposite_node(self, node_one, edge):
        if edge.node_one == node_one: return edge.node_two
        elif edge.node_two == node_one: return edge.node_one
        else: raise InvalidGraphException("The input edge to the function be not connected to the node_one also inputted.")
    
    def get_synonymous_words(self, word, permitted_level=1):
        # Get the necessary first informations
        visited_nodes, levels_dictionary, current_level, og_node = [], {}, 0, self.node_dictionary.word_to_node[word]
        return_list = []
        # First, mark the current node as visited, and push it to the stack:
        visited_nodes.append(og_node)
        levels_dictionary[current_level] = [og_node]
        # and then while we are lower than the permitted level (or there are no new nodes, whichever comes first)
        while (current_level < permitted_level and len(levels_dictionary[current_level]) != 0):
            # You would get increase the current_level
            current_level += 1
            # And then you would make the new level
            new_level_array = []
            for old_node in levels_dictionary[current_level - 1]:
                # Get the synset edges that are connected to that node
                connecting_synset_edges = old_node.list_of_synset_edges
                # Get the opposite nodes that are not visited
                connecting_nodes = [self.get_opposite_node(old_node, edge) for edge in connecting_synset_edges]
                connecting_nodes = [node for node in connecting_nodes if node not in visited_nodes]
                # and then make the new_level_array and visited extend to contain it
                new_level_array.extend(connecting_nodes)
                visited_nodes.extend(connecting_nodes)
            # And then set the current_level to be new_level_array in the dict
            levels_dictionary[current_level] = new_level_array
            return_list.extend(new_level_array)
        return_list = [node.word for node in return_list]
        return return_list
    
    def get_antonymous_words(self, word):
        # Get the nodes
        og_node = self.node_dictionary.word_to_node[word]
        # Get the list of the antonym edges:
        antonym_edges = og_node.list_of_antonym_edges
        antonym_nodes = [self.get_synonymous_words(og_node, edge) for edge in antonym_edges]
        return_list = [node.word for node in antonym_nodes]
        return return_list
        
        
            


################################################################################################
######## -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #########
######## -=-=-=-=-=-=-=-=-=-=-=-= PART OF ANALYSIS FOR GRAPH =-=-=-=-=-=-=-=-=-=-=-=-= #########
######## -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #########
################################################################################################

def graph_analysis():
    # Making a new Adjective Graph
    new_adjective_graph = AdjectiveGraph()
    print(new_adjective_graph.get_antonymous_words('good'))
    print(new_adjective_graph.get_synonymous_words('good'))
    
graph_analysis()