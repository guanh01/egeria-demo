#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 28 14:03:10 2017

parse opencl html into a sequence of sentences; each item is in dict format.
{"title":*** , "href":***, "body":***, "state": 2} 

@author: huiguan
"""


import re, os
from bs4 import BeautifulSoup
import bs4
from Helper import decode_ascii, decode_utf8, get_script_path
from pprint import pprint



def clearTags(htmltext, tagNames = ['pre', 'h2', 'h3','h4','table','span'], classes = ["figure", "variablelist"]):

    for tagName in tagNames:
        codeTags = htmltext.find_all(tagName)
        for codeTag in codeTags:
            codeTag.clear()
    for c in classes:
        codeTags = htmltext.find_all(class_=c)
        for codeTag in codeTags:
            codeTag.clear()


    return htmltext

# get text data in unicode format, get_text() return unicode string
def getText(htmltext):

    text = htmltext.get_text().strip()

    return text

def traverseHtml(blocks, htmltext, state = 1):
    for child in htmltext.children:
        if child.name == "div" and child.has_attr("class") and 'section' in child.get('class'):
            headtag = child.find(re.compile('^h\d+'))
            if headtag==None:
                continue
            atag = headtag.find("a")
            title = headtag.get_text() # get the headline of the section
            href = atag["id"]
            #print title, href
            body = getText(clearTags(child))
            
            blocks.append({"title": title, "href": href, "body": body, "state": state})

            
        
        

def parser(filename):
    
    text = decode_utf8(open(filename, 'r').read())
    soup = BeautifulSoup(text,"lxml")
    htmltext = soup.find(class_="article")
    blocks = []
    traverseHtml(blocks, htmltext)
    print "block length: ", len(blocks)  
    return blocks     


if __name__ == '__main__':
    from Config import guidename
    print "cwd:", os.getcwd()
    titles = parser(guidename)
    pprint(titles[:10])
    
