# -*- coding: utf-8 -*-
"""
Created on Mon Sep 26 20:53:33 2016
helper functions
@author: huiguan
"""
import pickle, os, json, re, string, sys
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem.snowball import SnowballStemmer
stemmer = SnowballStemmer("english")

from nltk.stem import WordNetLemmatizer
wordnet_lemmatizer = WordNetLemmatizer()

def normalize_verb(verb):
    return unicode(wordnet_lemmatizer.lemmatize(verb.lower(),pos='v'))
    
def normalize_noun(noun):
    return unicode(wordnet_lemmatizer.lemmatize(noun.lower(),pos='n'))


def save_pickle(to_saved, dirname, filename):
	print "save pickle to:", os.path.join(dirname, filename)
	return pickle.dump(to_saved, open(os.path.join(dirname, filename),'w') )    
    
def check_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def save_json(to_saved, dirname, filename):
    with open(os.path.join(dirname, filename), 'w') as outfile:
        outfile.write(json.dumps(to_saved, indent=4, sort_keys = True))
        
def load_pickle(dirname, filename):
    return pickle.load(open(os.path.join(dirname, filename), 'r'))
    
def decode_utf8(s, encoding="utf8", errors="ignore"):
    return s.decode(encoding=encoding, errors=errors)
    
def encode_utf8(s, encoding="utf8", errors="ignore"):
    return s.encode(encoding=encoding, errors=errors)
    
def encode_ascii(s, encoding="ascii", errors="ignore"):
    return s.encode(encoding=encoding, errors=errors)

def decode_ascii(s, encoding="ascii", errors="ignore"):
    return s.decode(encoding=encoding, errors=errors)    

def good_token(token):
    stoplist = stopwords.words('english')
    puncts = re.sub('-', '', string.punctuation) 
    if token in stoplist:
        return False
    if any(c in token for c in puncts):
        return False
    if re.search('[a-z]', token) == None:
        return False
    return True
    
def sents2tokens(sents):

    texts = [[stemmer.stem(word) for word in word_tokenize(sent.lower()) if good_token(word)] for sent in sents]
    return texts

def sent2tokens(sent):

    text = [stemmer.stem(word) for word in word_tokenize(sent.lower()) if good_token(word)] 
    return text

def docs2vecs(queries, dictionary=None, model=None):
    if dictionary==None or model ==None:
        raise Exception('dictionary or model is None.')
    queriesTokens = sents2tokens(queries)    
    queriesBow = [dictionary.doc2bow(text) for text in queriesTokens]
    queriesVec = model[queriesBow]  
    return queriesVec

def get_script_path():
    return os.path.dirname(os.path.realpath(sys.argv[0]))
