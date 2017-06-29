# -*- coding: utf-8 -*-
"""
Created on Sat Oct  8 21:32:11 2016
query engine return html
@author: huiguan
"""


from Helper import loadPickle, sents2tokens
from gensim import models, similarities, corpora
from nltk.stem.snowball import SnowballStemmer
stemmer = SnowballStemmer("english")
import re
from Config import similarity_threshold

from bs4 import BeautifulSoup
from Config import dictionary_filename, model_filename


class QueryEngineHtml(object):
    
    def __init__(self, models_folder):
        self.models_folder = models_folder
        self.themodel = loadPickle(dirname= models_folder, filename=model_filename)
        self.dictionary = loadPickle(dirname = models_folder, filename=dictionary_filename)  
        
  
    def issues2query(self, issues, keys = {'title', 'description', 'optimization'}):
        queryDocs = []
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
            queryDocs.append(queryDoc)
#            print "Performance issue: "
#            print '\t'+'title: \t'+issue['title']
#            print '\t'+'queryDoc: \t'+ queryDoc+'\n'
#            
        return queryDocs

    def docs2vecs(self, queryDocs):
        queriesTokens = sents2tokens(queryDocs)    
        queriesBow = [self.dictionary.doc2bow(text) for text in queriesTokens]
        queriesVec = self.themodel[queriesBow]  
        return queriesVec




    def traverseHtml(self, htmltext, index):
        for child in htmltext.children:
            if child.name=='div':
                if 'topic' in child['class']:
                    # head
                    #head = child.find(re.compile('^h\d')).get_text() # get the headline of the section
                    #print prefix+head
                    self.traverseHtml(child, index)
                    
                elif 'body' in child['class']:
                    # contain sentences
                    relevantFlag = False
                    lis = child.ul.children
                    for li in lis:
                        sent = li.string.strip()
                        #print li
                        if len(sent):
                            #print "sent: "+ sent
                            sentsVec = self.docs2vecs([sent])
                                
                            sims = index[sentsVec]
                            #print sims[0]
                            for v in sims[0]:
                                if v>= similarity_threshold:
                                    li['class'] = ['li', 'highlight']
                                    
                                    relevantFlag = True
                    if not relevantFlag:
                        child.decompose()

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
    def performQuery(self, issues, indexfilename):
        
        queryDocs = self.issues2query(issues)
    
        queriesVec = self.docs2vecs(queryDocs)
        index = similarities.MatrixSimilarity(queriesVec, num_features = len(self.dictionary))

        soup = BeautifulSoup(open(indexfilename), "lxml")
        htmltext = soup.find('article') # id="contents"
        
        self.traverseHtml(htmltext, index) 
        self.simplifyHtml(htmltext)     
    
        navTag = soup.find('nav')
        contentTag = soup.find(id='contents-container')
        if not htmltext.find('ul'):
            # if no sents found
            htmltext.decompose()
            ptag=soup.new_tag('p')
            ptag.string = "No relevant sentences found!"
            contentTag.append(ptag)
        
        res = u"""{% extends "base.html" %} \n """
        res += u"{% block sitenav %}\n" + unicode(navTag) +  u"\n {% endblock %} \n"
        res += u"{% block content %}\n" + unicode(contentTag)+ u'\n {% endblock %} \n'
                
        
        return res