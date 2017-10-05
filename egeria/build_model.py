# -*- coding: utf-8 -*-
"""
Created on Sun Oct 16 15:24:59 2016

create dictionary and models

@author: huiguan
"""



from bs4 import BeautifulSoup
from helper import sents2tokens, check_directory, save_pickle
from gensim import models, corpora
from egeria import settings 
import os


def buildModel( sentsBow, dictionary = None, model='tfidf', num_topics = 20):

    if model=='lda':     
        themodel = models.LdaModel(sentsBow, id2word=dictionary, num_topics = num_topics)

    elif model=='lsi':
        themodel = models.LsiModel(sentsBow, id2word=dictionary, num_topics = num_topics)
    
    elif model == "rp":
        themodel = models.RpModel(sentsBow, num_topics= num_topics)
    
    else:
        themodel = models.TfidfModel(sentsBow)
    
    return themodel

def buildDictionary( texts):
    dictionary = corpora.Dictionary(texts)
    # remove some items from the dict
    dictionary.filter_extremes(no_below=2, no_above=0.5, keep_n= None)
    return dictionary



def collectSents( filename):
    sents = []
    soup = BeautifulSoup(open(filename,'r'), 'lxml')
    contentTag = soup.find('article')
    sentsTag = contentTag.find_all('li')
    for sentTag in sentsTag:
        sent = unicode(sentTag.string).strip()
        sents.append(sent)
    return sents
    
    
def build(template_dir, model_dir):
    """Save tfidf model and dictionary built from a html file into model_dirname.
     Args:
       template_dir: the directory that saved the two html files, summary.html, raw.html
       model_dir: the directory to save the dictionary and tfidf model
    """
    filename = os.path.join(template_dir, settings.SUMMARY_HTML)
    if not os.path.isfile(filename):
        raise IOError("Error! file doesn't exit:", filename)
                    
    sents = collectSents(filename)
    allsents = collectSents(os.path.join(template_dir, settings.RAW_HTML))
    
    print "Build dict and models with: sents# = %d, allsents# = %d" %(len(sents), len(allsents))
    
    # use sents to build dictionary
    sentsTokens = sents2tokens(sents)
    dictionary = buildDictionary(sentsTokens)
    
    # use all sents to build model
    allsentsTokens = sents2tokens(allsents)
    sentsBow = [dictionary.doc2bow(sentTokens) for sentTokens in allsentsTokens]
    themodel = buildModel(sentsBow, model='tfidf')
    
    check_directory(model_dir)
    
    save_pickle(dictionary, model_dir, filename=settings.DICTIONARY_FILE)
    save_pickle(themodel, model_dir, filename=settings.MODEL_FILE)


