from math import pi
import dolphin
from time import sleep
import pickle
from icecream import ic
from random import choice
import os
from pathlib import Path
from colorama import Fore, Style
from tqdm import tqdm
from rich.progress import track



def print_red(text):
    print(f"{Fore.RED}{text}{Style.RESET_ALL}")

def print_green(text):
    print(f"{Fore.GREEN}{text}{Style.RESET_ALL}")



CORPUS_PATH = Path(__file__).resolve().with_name("original_corpus.pkl")

def word_cleaner(word):
    # if the word is longer than 8 characters
    if len(word) > 5:
        return False
    # if the word is shorter than 3 characters
    if len(word) < 3:
        return False
    # if the word contains a number
    if any(char.isdigit() for char in word):
        return False
    # if the word contains an underscore
    if "_" in word:
        return False
    # if the word contains a dash
    if "-" in word:
        return False
    # if the word passes all the tests
    else:
        return True
    
# load the corpus from the pickle file
with open(CORPUS_PATH, 'rb') as f:
    corpus = pickle.load(f)
    verbs = corpus['verbs']
    nouns = corpus['nouns']
    adjs = corpus['adjectives']

ic(len(verbs))
ic(len(nouns))
ic(len(adjs))

print("Cleaning verbs...")
verbs = [verb.lower() for verb in verbs if word_cleaner(verb)]
print("Cleaning nouns...")
nouns = [noun.lower() for noun in nouns if word_cleaner(noun)]
print("Cleaning adjectives...")
adjs = [adj.lower() for adj in adjs if word_cleaner(adj)]

ic(len(verbs))
ic(len(nouns))
ic(len(adjs))


def clean_wordlist(wordlist):
    cleaned_words = []
    for word in track(wordlist):
        output = dolphin.run(word)
        dolphin.flush()
        if "[PASS]" in output:
            print_green(f"{word} {output}")   
        elif "[FAIL]" in output:
            print_red(f"{word} {output}")
            cleaned_words.append(word)
            
        
        else:
            print("!!!Something went wrong entirely!!!")
            print(output)
    return cleaned_words

clean_verbs = clean_wordlist(verbs)
clean_adj = clean_wordlist(adjs)
clean_nouns = clean_wordlist(nouns)

# save them to cleaned_corpus.pkl
cleaned_corpus = {
    "verbs": clean_verbs,
    "nouns": clean_nouns,
    "adjectives": clean_adj
}
with open("cleaned_corpus.pkl", "wb") as f:
    pickle.dump(cleaned_corpus, f)