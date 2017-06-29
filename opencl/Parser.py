#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 28 14:03:10 2017

parse opencl html into a sequence of sentences; each item is in dict format.
{"title":*** , "href":***, "body":***, "state": 2} 

@author: huiguan
"""


import re
from bs4 import BeautifulSoup
from Helper import decode_ascii, decode_utf8, get_script_path



def clearTags(htmltext):
    # remove title
    tags = htmltext.find_all(re.compile(r'h\d'))
    for tag in tags:
        tag.clear()
        
    # remove other tag names with certain classes
    tagClasses = ['figure', 'table','code']
    for tagClass in tagClasses:
        codeTags = htmltext.find_all(class_=tagClass)
        for codeTag in codeTags:
            codeTag.clear()
    
    # remove other tag names with vertain tag names        
    tagNames = ['table', 'code', 'pre', 'figure']
    for tagName in tagNames:
        codeTags = htmltext.find_all(tagName)
        for tag in codeTags:
            tag.clear()

    return htmltext

# get text data in unicode format, get_text() return unicode string
def getText(htmltext):
    text = htmltext.get_text().strip()
    text = re.sub("\s+", " ", text)
    return text

# extract all the navigation ref
def extractTitles(soupRaw):
    headlines = soupRaw.find_all(class_=re.compile(r'(head\dTOC)|(chapterTOC)'))
    # go through headlines 
    titles = []
    state = 1
    print "headlines length: ", len(headlines)
    for i in xrange(len(headlines)):
        htag = headlines[i]
        atag = htag.find('a', href=True)
        href = atag['href']
        name = href.split('#')[-1]
        title = htag.get_text().strip()
        #print title
        if "Chapter" in title:
            # it is a chapter title
            state = 1
            titles.append({"href": name, "title": title, "state": state})
        else:
            # it is a subsection, and followed by a chapter
            if state == 1:
                # layer 2 section should contain number in title name
                nums = re.match('(\d+\.)+\d+', title)
                if not nums:
                    print "Error! Cannot find numbers from title: %s" %(title)
                    break
                nums = nums.group().split('.')
                if len(nums)!=2:
                    print "Error! Chapter not followed by section: %s" %(title)
                    break
                else:
                    state = 2
                    # create a ul list follow the chapter div
                    titles.append({"href":name, "title": title, "state": state})

            elif state == 2:
                    # if the previous section is section 1.1, check if this section is 1.2 or 1.1.1 
                    nums = re.match('(\d+\.)+\d+', title)
                    if not nums:
                        print "Error! Cannot find numbers from title: %s" %(title)
                        break
                    nums = nums.group().split('.')
                    if len(nums)==2:
                        # it is section 1.2
                        titles.append({"href":name, "title": title, "state": state})
                    elif len(nums)==3:
                        # it is section 1.1.1
                        state=3
                        titles.append({"href":name, "title": title, "state": state})
                    else:
                        print "Error! section not followed by section: %s" %(title)
                        break
            elif state == 3:
                # if the previous section is section 1.1.1, check if this section is 1.2 or 1.1.2 or 1.1.1.1
                nums = re.match('(\d+\.)+\d+', title)
                if not nums:
                    # it doesn't contain numbers, so this section is 1.1.1.1
                    state = 4
                    titles.append({"href":name, "title": title, "state": state})
                else:
                    nums = nums.group().split('.')
                    if len(nums)==2:
                        # go back to upper section
                        state = 2
                        titles.append({"href":name, "title": title, "state": state})
                    elif len(nums)==3:
                        titles.append({"href":name, "title": title, "state": state})
                    else:
                        print "Error! section not followed by section: %s" %(title)
                        break
            elif state==4:
                # if the previous section is section 1.1.1.1
                nums = re.match('(\d+\.)+\d+', title)
                if not nums:
                    # it doesn't contain numbers, so this section is 1.1.1.2
                   titles.append({"href":name, "title": title, "state": state})
                else:
                    nums = nums.group().split('.')
                    if len(nums)==3:
                        state=3
                        titles.append({"href":name, "title": title, "state": state})
                    elif len(nums)==2:
                        state = 2
                        titles.append({"href":name, "title": title, "state": state})
                    else:
                        print "Error! section not followed by section: %s" %(title)
                        break
            else:
                print "Error! state=%d, section: %s" %(state, title)
                
    return titles


def extractContents(titles, text):
    for i in xrange(len(titles)):
        hrefi = titles[i]['href']
        patterni = re.compile("<a\s+name\s*=\s*\"\s*"+ hrefi + "\s*\"")
        resi= patterni.search(text)
        if not resi:
            print "Error! Cannot find hrefi: "+hrefi
            break
        start = resi.start()
        
        if i<len(titles)-1:
            hrefj = titles[i+1]['href']
            
        else:
            hrefj = "50401311_pgfId-224076"
            
        patternj = re.compile("<a\s+name\s*=\s*\"\s*"+ hrefj + "\s*\"")
        resj = patternj.search(text)
        end = resj.start()
        content = BeautifulSoup(text[start:end], 'lxml')
           
        #title = content.find('head').get_text().strip()
        title = titles[i]["title"]       
        
        body = getText(clearTags(content))
        newbody = cleanTitleFromBody(body, title)
        titles[i]["body"] = newbody
        
        
        
            
def cleanTitleFromBody(body, title):
    tokens = titleTokens(title)
    bodyTokens=body.split()
    for i in xrange(len(bodyTokens)):
        btoken = bodyTokens[i].lower()
        if btoken not in tokens:
            return " ".join(bodyTokens[i:])
        else:
            tokens.remove(btoken)
    return ""

def titleTokens(title):
    tokens = title.lower().split() 
    return tokens
                

def parser(filename):
    
    text = decode_utf8(open(filename, 'r').read())
    soupRaw = BeautifulSoup(text,"lxml")
    
    titles =  extractTitles(soupRaw) 
    extractContents(titles, text)
   
    print "titles length: ", len(titles)  
    return titles     


if __name__ == '__main__':
    from Config import guidename
    print os.getcwd()
    titles = parser(guidename)
    print titles[:1]
    
