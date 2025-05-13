import yaml
from nltk.corpus import wordnet
from random import choice
def get_word_list(pos):
    words = set()
    for synset in wordnet.all_synsets(pos):
        for lemma in synset.lemmas():
            words.add(lemma.name())
    return list(words)

# Get lists of verbs, nouns, and adjectives
verb_list = get_word_list('v')  # 'v' stands for verb
noun_list = get_word_list('n')  # 'n' stands for noun
adj_list = get_word_list('a')   # 'a' stands for adjective
corpus = {'verbs': verb_list, 'nouns': noun_list, 'adjectives': adj_list}

# save the corpus as a pickle file
import pickle
with open('corpus.pkl', 'wb') as f:
    pickle.dump(corpus, f)

# load the corpus from the pickle file
import pickle
from time import perf_counter
t0 = perf_counter()
with open('corpus.pkl', 'rb') as f:
    corpus = pickle.load(f)
    verb_list = corpus['verbs']
    noun_list = corpus['nouns']
    adj_list = corpus['adjectives']
print(f"Loaded corpus in {perf_counter()-t0:.2f} seconds")



def generate_filename():
    if choice([True, False]):
        return choice(adj_list) + "_" + choice(noun_list) + ".mkv"
    else:
        return choice(verb_list) + "ing_" + choice(noun_list) + ".mkv"
    
    

for i in range(100):
    print(generate_filename())
    