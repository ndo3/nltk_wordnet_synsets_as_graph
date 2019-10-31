import json
import spacy
import numpy as np
from random import sample

# import Logistic Regression stuff
from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import LinearRegression
# import SVM stuff
from sklearn import svm
from sklearn.gaussian_process.kernels import RBF
# import DictVectorizer for space saving
from sklearn.feature_extraction import DictVectorizer
# import data sciency stuff
import matplotlib.pyplot as plt

nlp_en = spacy.load("en_core_web_lg")
v = DictVectorizer(sparse=False)

def import_all_the_necessary_stats(word_senses_path, word_related_words_path, word_antonyms_path, word_idfs_path):
    with open(word_senses_path, "r") as word_senses, open(word_related_words_path, "r") as word_related_words, open(word_antonyms_path, "r") as word_antonyms, open(word_idfs_path, "r") as word_idfs:
        senses_loaded, related_loaded, antonym_loaded, idf_loaded = json.load(word_senses), json.load(word_related_words), json.load(word_antonyms), json.load(word_idfs)
    return senses_loaded, related_loaded, antonym_loaded, idf_loaded

def import_list_from_text(list_of_paths):
    list_of_words = []
    for path in list_of_paths:
        with open(path, "r") as another_file:
            content = another_file.readlines()
        content = [x.strip() for x in content]
        for word in content:
            if word not in list_of_words: list_of_words.append(word)
    return list_of_words

def import_all_submissions(positive_path, negative_path_happy, negative_path_supportingsupporters):
    # Getting all the positive examples
    with open(positive_path, "r") as positive_file:
        positive_data = json.load(positive_file)
        if len(positive_data) > 1000:
            positive_data = sample(positive_data, 1000)
    # Getting all the negative examples
    with open(negative_path_happy, "r") as happy_file, open(negative_path_supportingsupporters, "r") as supportingsupporters_file:
        negative_data = json.load(supportingsupporters_file)
        happy_data = json.load(happy_file)
        negative_data.extend(sample(happy_data, 800-67))
    return positive_data, negative_data

def deal_with_each_datapoint(key, hedges, absolutist_adverbs_and_pronouns, senses_dict, related_dict, antonym_dict, idfs_dict):
    parsed = nlp_en(key)
    datapoint_dict = {}
    # The first attribute is the length of the sentence
    # datapoint_dict['len'] = len(key)
    # This part is to deal with all the hedges
    for hedge in hedges:
        if hedge in key:
            if hedge not in datapoint_dict: datapoint_dict[hedge] = 1
            else: datapoint_dict[hedge] += 1
    for token in parsed:
        lowered = token.text.lower()
        running_number_of_adjectives = 0
        running_numbers_of_senses, running_numbers_of_related_words, running_numbers_of_antonyms, running_numbers_of_idfs = [], [], [], []
        # Processing the datapoints that are the absolutist adverbs and pronouns
        if lowered in absolutist_adverbs_and_pronouns:
            if lowered not in datapoint_dict:
                datapoint_dict[lowered] = 1
            else:
                datapoint_dict[lowered] += 1
        # If the pos_ is adjective, then we are going to do several things:
        # (0) zero, update the number of adjectives in this sentence
        # (1) first, count the presence of the adjective in the sentence
        # (2) two, update the running numbers, so that we can calculate the standard deviation mean later
        if token.pos_ == "ADJ":
            if lowered in senses_dict and lowered in related_dict and lowered in antonym_dict and lowered in idfs_dict:
                # (0):
                running_number_of_adjectives += 1
                # (1):
                if token.text.lower() not in datapoint_dict: datapoint_dict[lowered] = 1
                else: datapoint_dict[lowered] += 1
                # (2):
                running_numbers_of_senses.append(senses_dict[lowered])
                running_numbers_of_related_words.append(related_dict[lowered])
                running_numbers_of_antonyms.append(antonym_dict[lowered])
                running_numbers_of_idfs.append(idfs_dict[lowered])
    # And then after we have dealt with all the words, we will make new features based on the information that we collected
    if running_number_of_adjectives != 0:
        datapoint_dict["num_adjectives"] = running_number_of_adjectives
        # # Updating all the mean fields
        datapoint_dict["average_num_of_senses"] = np.mean(running_numbers_of_senses)
        datapoint_dict["average_num_of_related_words"] = np.mean(running_numbers_of_related_words)
        datapoint_dict["average_number_of_antonyms"] = np.mean(running_numbers_of_antonyms)
        datapoint_dict["average_idf"] = np.mean(running_numbers_of_idfs)
        # Updating all the median fields
        datapoint_dict["median_num_of_senses"] = np.median(running_numbers_of_senses)
        datapoint_dict["median_num_of_related_words"] = np.median(running_numbers_of_related_words)
        datapoint_dict["median_number_of_antonyms"] = np.median(running_numbers_of_antonyms)
        datapoint_dict["median_idf"] = np.median(running_numbers_of_idfs)
        # Updating all the standard deviation fields
        datapoint_dict["std_num_of_senses"] = np.std(running_numbers_of_senses)
        datapoint_dict["std_num_of_related_words"] = np.std(running_numbers_of_related_words)
        datapoint_dict["std_number_of_antonyms"] = np.std(running_numbers_of_antonyms)
        datapoint_dict["std_idf"] = np.std(running_numbers_of_idfs)
    return datapoint_dict


def process_julia_data(list_of_hedges, list_of_adverbs_and_pronouns, senses_loaded, related_loaded, antonym_loaded, idf_loaded):
    data_path = "mturk_stats.json"
    # Load all the important things
    with open(data_path, "r") as data_file:
        # Loading the data - list of dictionaries
        all_data, all_labels_mean, all_labels_std = [], [], []
        # Also have to account for testing data
        all_test_data, all_test_mean, all_test_std = [], [], []
        data = json.load(data_file)
        for i, key in enumerate(data):
            if data[key][0] > 0.4: mean_value = 1
            else: mean_value = 0
            if data[key][1] < 0.5: std_value = 1
            else: std_value = 0
            datapoint = deal_with_each_datapoint(key, list_of_hedges, list_of_adverbs_and_pronouns, senses_loaded, related_loaded, antonym_loaded, idf_loaded)
            if i < len(data) and std_value == 1:
                all_data.append(datapoint)
                all_labels_mean.append(mean_value)
                all_labels_std.append(std_value)
            # else if i >= len(data)*3/4 and std_value == 1:
            else:
                all_test_data.append(datapoint)
                all_test_mean.append(mean_value)
                all_test_std.append(std_value)

    transformed_train = v.fit_transform(all_data)
    transformed_test = v.transform(all_test_data)
    print("Running Logistic Regression...")
    lr_model = LogisticRegression(solver='lbfgs').fit(transformed_train, all_labels_mean)
    # model_score = model.score(transformed_test, all_test_mean)
    model_score = lr_model.score(transformed_train, all_labels_mean)
    print("Logistic Regression Model score:")
    print(model_score)
    print("Running SVM with Linear Kernel...")
    svm_model = svm.LinearSVC()
    svm_model.fit(transformed_train, all_labels_mean)
    prediction = svm_model.predict(transformed_train)
    print("SVM with Linear Kernel Model score:")
    print(calculate_correctness(prediction, all_labels_mean))
    print("\n\n")
    return lr_model, svm_model
    # Loop through the stuff

def draw_graph(lr_model, svm_model, vectorizer, senses_loaded, related_loaded, antonym_loaded, idf_loaded):
    vectorizer_name_to_index = vectorizer.vocabulary_
    vectorizer_index_to_name = {vectorizer_name_to_index[k]: k for k in vectorizer_name_to_index}
    # Getting the coefficients
    logistic_regression_coefficients = lr_model.coef_[0]
    svm_linear_coefficients = svm_model.coef_[0]
    # Make mapping from name to index
    name_to_lr_coefficients = {k: logistic_regression_coefficients[vectorizer_name_to_index[k]] for k in vectorizer_name_to_index}
    name_to_svm_coefficients = {k: svm_linear_coefficients[vectorizer_name_to_index[k]] for k in vectorizer_name_to_index}
    # print out things that im interested
    print(name_to_lr_coefficients["average_num_of_senses"])
    print(name_to_lr_coefficients["average_num_of_related_words"])
    print(name_to_lr_coefficients["average_number_of_antonyms"])
    print(name_to_lr_coefficients["num_adjectives"])
    print(name_to_lr_coefficients["average_idf"])
    print(name_to_lr_coefficients["median_num_of_senses"])
    print(name_to_lr_coefficients["median_num_of_related_words"])
    print(name_to_lr_coefficients["median_number_of_antonyms"])
    print(name_to_lr_coefficients["median_idf"])
    # sorted dicts
    sorted_name_to_lr_coefficients = sorted(name_to_lr_coefficients.items(), key=lambda kv: -kv[1])
    sorted_name_to_svm_coefficients = sorted(name_to_svm_coefficients.items(), key=lambda kv: -kv[1])
    coeff_list, related = [], []
    for word, coeff in sorted_name_to_lr_coefficients:
        if coeff == 0:
            break
        if word in related_loaded:
            coeff_list.append(coeff)
            related.append(related_loaded[word])
    # plotting it
    plt.plot(range(len(coeff_list)), coeff_list)
    plt.plot(range(len(coeff_list)), related)
    plt.legend(['coefficients', 'number of related words'])
    plt.show()



def calculate_correctness(ar, br):
    corr = 0.
    for i, a in enumerate(ar):
        if a == br[i]:
            corr += 1.
    return corr/len(ar)

def welcome_peoples_input():
    adverbs_and_pronouns_data = ["adverbs_of_degree.txt", "adverbs_of_frequency.txt", "adverbs_of_stance.txt", "interrogative_pronouns.txt", "pronouns_of_degree.txt", "relative_pronouns.txt"]
    adverbs_and_pronouns_data = ["../nlpmh/stuff_with_data/" + i for i in adverbs_and_pronouns_data]
    ## This part is for the hedging stuff
    hedging_data = ["relational_hedges.txt", "propositional_hedges.txt"]
    hedging_data = ["../nlpmh/stuff_with_data/" + i for i in hedging_data]
    list_of_adverbs_and_pronouns = import_list_from_text(adverbs_and_pronouns_data)
    # Importing list of hedges as well
    list_of_hedges = import_list_from_text(hedging_data)
    senses_loaded, related_loaded, antonym_loaded, idf_loaded = import_all_the_necessary_stats("adj_to_num_associated_senses.json", "adj_number_of_synsets_threedegs.json", "adj_number_of_antonyms.json", "adj_to_idf.json")
    model, svm_model = process_julia_data(list_of_hedges, list_of_adverbs_and_pronouns, senses_loaded, related_loaded, antonym_loaded, idf_loaded)
    draw_graph(model, svm_model, v, senses_loaded, related_loaded, antonym_loaded, idf_loaded)
    input_welcoming = True
    index = 0
    data, label = [], []
    while input_welcoming:
        if index == 0:
            print("Type your sentence here. If you want to Quit, type q.\n")
            index += 1
        peopleinput = input("> ")
        if peopleinput == 'q':
            input_welcoming = False
            print("Thanks for participating! Your data is duly collected and will help make our product better :)")
            with open("symposium.json", "r") as to_read_file:
                current_data = json.load(to_read_file)
            for i, entry in enumerate(data):
                current_data[entry] = label[i]
            with open("symposium.json", "w") as to_write_file:
                # print(current_data)
                json.dump(current_data, to_write_file)
            print("\n\n\n")
        else:
            datapoint = v.transform([deal_with_each_datapoint(peopleinput, list_of_hedges, list_of_adverbs_and_pronouns, senses_loaded, related_loaded, antonym_loaded, idf_loaded)])
            out = model.predict(datapoint)
            print("-=-=-=-=-=-=")
            if out[0] == 0: print("Logistic Regression: Not absolutist")
            else: print("Logistic Regression: Absolutist")
            svm_out = svm_model.predict(datapoint)
            if svm_out[0] == 0: print("SVM Regression: Not absolutist")
            else: print("SVM with Linear Kernel: Absolutist")
            print("-=-=-=-=-=-=")
            correct_input = input("Is this absolutist? [Yes, No, y, n, yeet (y), yeehaw (y)] ")
            if correct_input.lower() in ['yes', 'no', 'y', 'n', 'yeet', 'yeehaw']:
                data.append(peopleinput)
                if correct_input.lower() in ["yes", 'y', 'yeet', 'yeehaw']:
                    true_value = 1
                else:
                    true_value = 0
                label.append(true_value)
                print("Data collected. Thanks! Moving on...\n")
            else: print("Invalid input. Data not collected. Moving on...\n")



def process_each_submission(positive_data, negative_data):
    for submission in positive_data:
        all = submission['title'] + ' ' + submission['selftext']
        print(all)

# positive_data, negative_data = import_all_submissions("../nlpmh/data/original_submissions.json", "../nlpmh/data/original_happy_submissions.json", "../nlpmh/data/original_supporters_submissions.json")
# process_each_submission(positive_data, negative_data)

# process_julia_data()
welcome_peoples_input()
