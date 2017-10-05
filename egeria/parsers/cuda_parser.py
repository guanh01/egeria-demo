#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 28 14:03:10 2017

parse html into a sequence of sentences; each item is in dict format.
{"title":*** , "href":***, "body":***, "state": 2} 

@author: huiguan
"""


import re, os
from bs4 import BeautifulSoup
from egeria.helper import decode_ascii, decode_utf8
# from pprint import pprint



def _clearTags(htmltext, tagNames = ['pre', 'h2', 'h3','h4','table','span']):
    for tagName in tagNames:
        codeTags = htmltext.find_all(tagName)
        for codeTag in codeTags:
            codeTag.clear()
    return htmltext


# get text data in unicode format, get_text() return unicode string
def _getText(htmltext):
    text = htmltext.get_text().strip()
    text = re.sub("\s+", " ", text)
    return text


def _traverseHtml(titles, htmltext, state =1):
    for child in htmltext.children:
        if child.name == "div" and 'topic' in child['class']:
            head = child.find(re.compile('^h\d')).get_text() # get the headline of the section
            
            if re.match(r'(\w\.)+', head): # head has to start with number, such as 3.2.1
                #print prefix+head
                item = {"title": head, "state": state, "href": child["id"]}
                body = ""
                for grandchild in child.children:
                    if grandchild.name=="div" and "body" in grandchild['class']:
                        body += " " +_getText(_clearTags(grandchild))
                item["body"] = body
                titles.append(item)
                _traverseHtml(titles, child, state=state + 1)

                


                    

def parse(filename):
    text = decode_utf8(open(filename, 'r').read())
    soup = BeautifulSoup(text,"lxml")
    htmltext = soup.find(id="contents")
    titles = []
    
    _traverseHtml(titles, htmltext)
   
    print "sequence length: ", len(titles)  
    return titles     


