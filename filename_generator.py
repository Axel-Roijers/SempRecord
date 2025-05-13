import pickle
from random import choice
import os
from pathlib import Path
MAX_WORD_LENGTH = 5
CORPUS_PATH = Path(__file__).resolve().with_name("original_corpus.pkl")

def generate_filename():
    # load the corpus from the pickle file
    with open(CORPUS_PATH, 'rb') as f:
        corpus = pickle.load(f)
        verbs = corpus['verbs']
        nouns = corpus['nouns']
        adjs = corpus['adjectives']
        
        #filter verbs nouns and adjectives to be less or equal to MAX_WORD_LENGTH
        
        verbs = [v for v in verbs if len(v) <= MAX_WORD_LENGTH]
        nouns = [n for n in nouns if len(n) <=MAX_WORD_LENGTH]
        adjs = [a for a in adjs if len(a) <=MAX_WORD_LENGTH]

        

    if choice([True, False]):
        return choice(adjs) + "_" + choice(nouns)
    else:
        return choice(verbs) + "ing_" + choice(nouns)
    
    
if __name__ == "__main__":
    # generate 20 filenames
    for i in range(80):
        print(generate_filename())
