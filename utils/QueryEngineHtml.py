# -*- coding: utf-8 -*-
"""
Created on Sat Oct  8 21:32:11 2016
query engine return html

Website gives response very slow. The reason is BeautifulSoup package is slow. 

17-09-21 22:11:41    Search by query: reduce memory latency
prepare htmltext 2.1501250267
prepare similar sents index 0.00196003913879
prepare response content 0.0789740085602
prepare return html 0.0720899105072

after move beautifulsoup library-related commands into init:

17-09-21 22:17:21    Search by query: reduce memory latency
prepare htmltext 5.00679016113e-06
prepare similar sents index 0.00949096679688
prepare response content 0.106106996536
prepare return html 0.0470700263977


@author: huiguan
"""

import copy 
from Helper import loadPickle, sents2tokens
from gensim import models, similarities, corpora
from nltk.stem.snowball import SnowballStemmer
stemmer = SnowballStemmer("english")
import re, time
import numpy as np

from bs4 import BeautifulSoup
#from Config import dictionary_filename, model_filename


class QueryEngineHtml(object):
    
    def __init__(self, models_folder, source_file):
        dictionary_filename = "dictionary.dict"
        model_filename = "themodel.model"
        self.models_folder = models_folder
        self.themodel = loadPickle(dirname= models_folder, filename=model_filename)
        self.dictionary = loadPickle(dirname = models_folder, filename=dictionary_filename)  
        
        self.source_file = source_file
        self.soup = BeautifulSoup(open(self.source_file), "lxml")
        
        self.htmltext = self.soup.find('article') # id="contents"
        self.navTag = self.soup.find('nav')
        self.contentTag = self.soup.find(id='contents-container')

        self.simIndex = self.buildSimIndex()
        print "Website is running"
        
  
    def issues2queries(self, issues, keys = {'title', 'description', 'optimization'}):
        queries = []
        for issue in issues:
            queryDoc = []
            for key in keys:
                if key not in issue:
                    continue
                if key=='title':
                    title = re.sub('(\d+\.)+', '', issue[key]).strip()+'.'
                    queryDoc.append(title)
                else:
                    queryDoc.append(issue[key])
            queryDoc = " ".join(queryDoc)
            queries.append(queryDoc)
#            print "Performance issue: "
#            print '\t'+'title: \t'+issue['title']
#            print '\t'+'queryDoc: \t'+ queryDoc+'\n'
#            
        return queries

    def docs2vecs(self, queries):
        queriesTokens = sents2tokens(queries)    
        queriesBow = [self.dictionary.doc2bow(text) for text in queriesTokens]
        queriesVec = self.themodel[queriesBow]  
        return queriesVec

    

    # def traverseHtml(self, htmltext, index, similarity_threshold):
    #     for child in htmltext.children:
    #         if child.name=='div':
    #             if 'topic' in child['class']:
    #                 # head
    #                 #head = child.find(re.compile('^h\d')).get_text() # get the headline of the section
    #                 #print prefix+head
    #                 self.traverseHtml(child, index, similarity_threshold)
                    
    #             elif 'body' in child['class']:
    #                 # contain sentences
    #                 relevantFlag = False
    #                 lis = child.ul.children
    #                 for li in lis:
    #                     sent = li.string.strip()
    #                     #print li
    #                     if len(sent):
    #                         #print "sent: "+ sent
    #                         sentsVec = self.docs2vecs([sent])
                                
    #                         sims = index[sentsVec]
    #                         #print sims[0]
    #                         for v in sims[0]:
    #                             if v> similarity_threshold:
    #                                 li['class'] = ['li', 'highlight']
                                    
    #                                 relevantFlag = True
    #                 if not relevantFlag:
    #                     child.decompose()

    
                        
    def buildSimIndex(self):
        #print "Build simIndex with source file:", self.source_file
        htmltext = self.htmltext
        def traverseHtml(htmltext, sents):
            """get all the sentences in the HTML text"""
            for child in htmltext.children:
                if child.name=='div':
                    if 'topic' in child['class']:
                        traverseHtml(child, sents)
                        
                    elif 'body' in child['class']:
                        lis = child.ul.children
                        for li in lis:
                            sents.extend([li.string.strip() for li in lis if len(li.string.strip())])

        sents = [] # all the sents in the html
        traverseHtml(htmltext, sents)
        #print 'sents', len(sents)
        #print sents[:10]
        sentsVec = self.docs2vecs(sents)
        index = similarities.MatrixSimilarity(sentsVec, num_features = len(self.dictionary))
        return index 

    def getRetrievedSentsIndex(self, simIndex, issues, sim_thr=0.15):
        queries = self.issues2queries(issues)
        queriesVec = self.docs2vecs(queries)
        sims = simIndex[queriesVec]
        sims_max = np.max(sims, axis=0)
        indexes = [i for i, v in enumerate(sims_max) if v > sim_thr]
        #print len(indexes), indexes 
        return set(indexes)


    def traverseHtml(self, htmltext, indexes, ind=0):
        # if ind==0:
            #print 'id(htmltext)', htmltext
        for child in htmltext.children:
            if child.name=='div':
                if 'topic' in child['class']:
                    ind = self.traverseHtml(child, indexes, ind=ind)
                    
                elif 'body' in child['class']:
                    relevantFlag = False
                    lis = child.ul.children
                    for li in lis:
                        sent = li.string.strip()
                        if len(sent):
                            
                            if ind in indexes:
                                li['class'] = ['li', 'highlight']
                                relevantFlag = True
                                #print ind, sent 
                            ind+=1

                    if not relevantFlag:
                        child.decompose() 
        return ind 
                       


    """ Remove section title that doesn't contain relevant sentences"""                            
    def simplifyHtml(self, htmltext):
        ul = htmltext.find('ul')
        if ul:
            for child in htmltext.children:
                if child.name == 'div':
                    self.simplifyHtml(child)
        else:
            htmltext.decompose()                    
      
    #issues = report2issues(dirname = '../uploads', filename='trans_opt.nvvp.report.pdf')
    """ query(index.html, issues) = search_results.html"""
    def performQuery(self, issues, similarity_threshold):
        

        #duration = time.time()
        soup = self.soup #copy.deepcopy(self.soup) 
        navTag = self.navTag
        #print 'prepare copy', time.time() - duration 
        #htmltext = soup.find('article') # id="contents"
        #duration = time.time()
        contentTag = copy.deepcopy(self.contentTag)  #soup.find(id='contents-container')
        #print 'prepare deepcopy', time.time() - duration 

        duration = time.time()
        htmltext = [tag for tag in contentTag.contents if tag.name=='article'][0] #contentTag.find('article') # id="contents"
        
        #contentTag = copy.deepcopy(self.contentTag)
        #print 'prepare htmltext', time.time() - duration 

        #duration = time.time()
        indexes = self.getRetrievedSentsIndex(self.simIndex, issues, sim_thr=similarity_threshold)
        #print "prepare similar sents index", time.time() - duration 

        if len(indexes):
            # duration = time.time()
            self.traverseHtml(htmltext, indexes)
            self.simplifyHtml(htmltext)     
            # print "prepare response content", time.time() - duration 
    
        # duration = time.time()
        # if not htmltext.find('ul'):
        else: 
            # if no sents found
            htmltext.decompose()
            ptag=soup.new_tag('p')
            ptag.string = "No relevant sentences found!"
            contentTag.append(ptag)
        
        res = u"""{% extends "base.html" %} \n """
        res += u"{% block sitenav %}\n" + unicode(navTag) +  u"\n {% endblock %} \n"
        res += u"{% block content %}\n" + unicode(contentTag)+ u'\n {% endblock %} \n'
        # print "prepare return html", time.time() - duration 
        
        return res