# -*- coding: utf-8 -*-
"""
Created on Sun Oct 16 15:24:59 2016

create dictionary and models

@author: huiguan
"""



from bs4 import BeautifulSoup
from Helper import sents2tokens, checkDirectory, savePickle
from gensim import models, corpora
from Config import dictionary_filename, model_filename
import os


def buildModel(sentsBow, model='tfidf', num_topics = 20):
    global dictionary
    if model=='lda':     
        themodel = models.LdaModel(sentsBow, id2word=dictionary, num_topics=num_topics)

    elif model=='lsi':
        themodel = models.LsiModel(sentsBow, id2word=dictionary, num_topics = num_topics)
    
    elif model == "rp":
        themodel = models.RpModel(sentsBow, num_topics= num_topics)
    
    else:
        themodel = models.TfidfModel(sentsBow)
    
    return themodel

def buildDictionary(texts):
    dictionary = corpora.Dictionary(texts)
    # remove some items from the dict
    dictionary.filter_extremes(no_below=2, no_above=0.5, keep_n= None)
    return dictionary



def collectSents(filename):
    sents = []
    soup = BeautifulSoup(open(filename,'r'), 'lxml')
    contentTag = soup.find('article')
    sentsTag = contentTag.find_all('li')
    for sentTag in sentsTag:
        sent = unicode(sentTag.string).strip()
        sents.append(sent)
    return sents
    
    
def buildDictAndModels(html_dirname, model_dirname):
    filename = os.path.join(html_dirname, "index.html")
    
    if not os.path.isfile(filename):
        print "Error! file doesn't exit:", filename
        return
        
    sents = collectSents(filename)
    allsents = collectSents(os.path.join(html_dirname, "rawIndex.html"))
    
    print "Build dict and models with: Sents# = %d, allsents# = %d" %(len(sents), len(allsents))
    
    # use sents to build dictionary
    sentsTokens = sents2tokens(sents)
    dictionary = buildDictionary(sentsTokens)
    
    # use all sents to build model
    allsentsTokens = sents2tokens(allsents)
    sentsBow = [dictionary.doc2bow(sentTokens) for sentTokens in allsentsTokens]
    themodel = buildModel(sentsBow, model='tfidf')
    
    checkDirectory(model_dirname)
    
    savePickle(dictionary, model_dirname, filename=dictionary_filename)
    savePickle(themodel, model_dirname, filename=model_filename)

if __name__ == '__main__':
    buildDictAndModels()