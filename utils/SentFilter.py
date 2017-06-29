# -*- coding: utf-8 -*-
"""
Created on Sun Sep 25 23:08:42 2016
# NLP tools and domain knowledge to filter sentences
# input: string
# output: list of useful sents
@author: huiguan
"""


import re
from nltk.tokenize import sent_tokenize , word_tokenize
from nltk.stem.snowball import SnowballStemmer
stemmer = SnowballStemmer("english")
from nltk.stem import WordNetLemmatizer
wordnet_lemmatizer = WordNetLemmatizer()

from practnlptools.tools import Annotator
annotator=Annotator()
from Helper import encode_ascii

from pycorenlp import StanfordCoreNLP
nlp = StanfordCoreNLP('http://localhost:9000')
# Run the server using all jars in the current directory (e.g., the CoreNLP home directory)
# java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer [port] [timeout]


            

def normalize_verb(verb):
    return unicode(wordnet_lemmatizer.lemmatize(verb.lower(),pos='v'))
    
def normalize_noun(noun):
    return unicode(wordnet_lemmatizer.lemmatize(noun.lower(),pos='n'))

def sentFilter(text, filterMethod = 'egeria'):
    sents = [v for v in sent_tokenize(text) if len(word_tokenize(v))>1]
    if filterMethod =="":
    	return sents, sents, []
    	
    useful_sents, inSummary = filterOpenCl(sents, filterMethod)
    return useful_sents, sents, inSummary




def filterOpenCl(sents, filterMethod):
    #print "Filter by opencl..."
    useful_sents = []
    inSummary = [0]*len(sents)
    for sentidx in xrange(len(sents)):
        sent = sents[sentidx]
        if goodSent(sent, filterMethod):
            useful_sents.append(sent)
            inSummary[sentidx]=1
    return useful_sents, inSummary

def goodSent(sent, filterMethod):
    if filterMethod=="imperative" and isImperativeSentByDepParse(sent):
        return True
    elif filterMethod =="comparative" and isComparativeSent(sent):
        return True
    elif filterMethod =="keyword" and isKeywordInSents(sent):
        return True
    elif filterMethod =="purpose" and isSentSrlGood(sent):
        return True
    elif filterMethod =="subject" and isSentSubjectGood(sent):
        return True
    elif filterMethod =="keywordAll" and isAllKeywordInSents(sent):
        return True
    elif filterMethod =="egeria":
        # keyword-based filter
        if isKeywordInSents(sent):
            return True
        # dependency parsing-based filter
        output = nlp.annotate(encode_ascii(sent), \
                          properties={'annotators': 'tokenize, ssplit, pos, depparse','outputFormat': 'json'})
        if 'sentences' in output and len(output['sentences']):    
            dep_parse = output['sentences'][0]['collapsed-ccprocessed-dependencies']
            if isImperativeSentByDepParse(sent, dep_parse) or \
                isComparativeSent(sent, dep_parse) or  \
                isSentSubjectGood(sent, dep_parse):
                return True
        
        if isSentSrlGood(sent):
            return True
    return False
           
# "peak bandwidth",'peak throughput', 'result in',
from Config import keywords
def isKeywordInSents(sent, keywords = keywords):
    words_stems = [stemmer.stem(word) for word in word_tokenize(sent.lower())]
    appear_only_stem = [[stemmer.stem(w) for w in word_tokenize(p)] for p in keywords]
    sent_stems = ' '.join(words_stems)
    for kp in appear_only_stem:
        pattern = '\s'.join(kp)
        if re.search(pattern, sent_stems):
            return True
            
    return False


# dependency parsing

from Config import verbs_imperativesents
def isImperativeSentByDepParse(sent, dep_parse, verbose = False):
    # need to use the dependence parsing from standford corenlp
    if normalize_verb(word_tokenize(sent.lower())[0])=="use":
        return True
    # find the word that associate with root
    dependentsV = []
    for item in dep_parse:
        if item[u'dep'] == u'ROOT':
            v = (item[u'dependent'], item[u"dependentGloss"])
            if verbose:
                print item
        if item[u'dep'] == u"nsubj" :
            dependentsV.append((item[u'dependent'], item[u"dependentGloss"]))
            dependentsV.append((item[u'governor'], item[u"governorGloss"]))
            if verbose:
                print item
        if item[u'dep'] == u"nsubjpass":
            dependentsV.append((item[u'governor'], item[u"governorGloss"]))
            if verbose:
                print item
        if item[u'dep'] == u"advmod" and item[u'dependentGloss'].lower() == 'when':
        	dependentsV.append((item[u'governor'], item[u"governorGloss"]))
        	
    if v not in dependentsV and normalize_verb(v[1]) in verbs_imperativesents:
        return True
        
    
    return False    
    

from Config import words_comparativeSent
def isComparativeSent(sent, dep_parse, verbose = False):
    # need to use the dependence parsing from standford corenlp
    for item in dep_parse:
        if item[u'dep']== u"xcomp" and item[u'governorGloss'] in words_comparativeSent:
            if verbose:
                print item
            return True
    return False
            
        
from Config import subject_keywords
def isSentSubjectGood(sent, dep_parse):
    words = [normalize_noun(w) for w in subject_keywords]
    
    for item in dep_parse:
        if item[u'dep'] in [u"nsubj", u'nsubjpass'] and normalize_noun(item[u'dependentGloss']) in words:
            return True
    return False
    


# semantic role labeling
from Config import no_subject_keywords
def isSentSrlGood(sent):
    # if minimize in the sentence, it should be v+A1
    words_stems = [stemmer.stem(word) for word in word_tokenize(sent.lower())]
    for kw in no_subject_keywords:
        kw_stem = stemmer.stem(kw)
        if kw_stem not in words_stems:
            continue
        try:
            annotation = annotator.getAnnotations(sent)
        except:
            break
        srl = annotation['srl']
        for event in srl:
            if stemmer.stem(event['V'])==kw_stem:
                if 'A0' not in event:
                    return True
    return False



from Config import allKeywords
def isAllKeywordInSents(sent, keywords = allKeywords):
    words_stems = [stemmer.stem(word) for word in word_tokenize(sent.lower())]
    appear_only_stem = [[stemmer.stem(w) for w in word_tokenize(p)] for p in keywords]
    sent_stems = ' '.join(words_stems)
    for kp in appear_only_stem:
        pattern = '\s'+'\s'.join(kp)+'\s'
        if re.search(pattern, sent_stems):
            return True
    return False              
    

