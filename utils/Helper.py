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


def savePickle(to_saved, dirname, filename):
	print "save pickle to:", os.path.join(dirname, filename)
	return pickle.dump(to_saved, open(os.path.join(dirname, filename),'w') )    
    
def checkDirectory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def saveJson(to_saved, dirname, filename):
    with open(os.path.join(dirname, filename), 'w') as outfile:
        outfile.write(json.dumps(to_saved, indent=4, sort_keys = True))
        
def loadPickle(dirname, filename):
    return pickle.load(open(os.path.join(dirname, filename), 'r'))
    
def decode_utf8(s, encoding="utf8", errors="ignore"):
    return s.decode(encoding=encoding, errors=errors)
    
def encode_utf8(s, encoding="utf8", errors="ignore"):
    return s.encode(encoding=encoding, errors=errors)
    
def encode_ascii(s, encoding="ascii", errors="ignore"):
    return s.encode(encoding=encoding, errors=errors)

def decode_ascii(s, encoding="ascii", errors="ignore"):
    return s.decode(encoding=encoding, errors=errors)    

def goodToken(token):
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

    texts = [[stemmer.stem(word) for word in word_tokenize(sent.lower()) if goodToken(word)] for sent in sents]
    return texts

def sent2tokens(sent):

    text = [stemmer.stem(word) for word in word_tokenize(sent.lower()) if goodToken(word)] 
    return text


def get_script_path():
    return os.path.dirname(os.path.realpath(sys.argv[0]))
