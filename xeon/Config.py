#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 28 13:46:30 2017
congiguration
@author: huiguan
"""

folder_name = "xeon"

port = '5000'
host = '152.14.86.182'


similarity_threshold = 0.15
filterMethod = 'egeria'

guidename = "Best Practice Guide - Intel Xeon Phi - PRACE Research Infrastructure.html"
weblink = "http://www.prace-ri.eu/best-practice-guide-intel-xeon-phi-html/"


dictionary_filename = "dictionary.dict"
model_filename = "themodel.model"


keywords = {'better', 'best performance', 'higher performance', 
            'maximum performance', 'peak performance', 'improve the performance',
            'higher impact', 'more appropriate',  'should', 'high bandwidth', 'high throughput',
            'prefer','effective way', "one way to","the key to", "contribute to", 
            "can be used to", "can lead to", "reduce",  'can help', 'can be important','can be useful',
            'is important', "help avoid", 'can avoid',  'instead', 'is desirable',
            "good choice", 'ideal choice', 'good idea', 'good start', 'benefit', 'encouraged', \
            'has to be', 'have to be'}


verbs_imperativesents = {'use', 'avoid', 'create', 'make', 'map', 'align', 
                         'add', 'change', 'ensure', 'call', 'unroll', 'move',
                         'select', 'schedule', 'switch', 'transform', 'pack'} 

words_comparativeSent = {'prefer', 'best', 'faster', 'better','efficient', 'beneficial', 'appropriate'
                         'recommended', 'encouraged', 'leveraged', 'important', 'useful', 'required','controlled'}



subject_keywords = {'programmer', 'developer', 'application', 'solution', \
                    'algorithm', 'optimization', 'guideline', 'technique', \
                    'user', 'one'}


no_subject_keywords = {'maximize', 'minimize', 'recommend','accomplish', 'achieve', 'avoid'}

allKeywords = subject_keywords | no_subject_keywords | keywords | words_comparativeSent | verbs_imperativesents
