#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 28 14:09:50 2017
Build HTML: index.html, rawIndex.html
@author: huiguan
"""

import os
from nltk import sent_tokenize
from bs4 import BeautifulSoup
from egeria.sent_filter import filter_text 
from egeria.helper import check_directory
from egeria.settings import RAW_HTML, SUMMARY_HTML
from egeria.keywords import keywords_factory 


soup = BeautifulSoup('', 'lxml')

#stateDivClassDict={1: "topic concept nested0", 
#                2: "topic concept nested1",
#                3: "topic concept nested2",
#                4: "topic concept nested3"}
def getDivClassByState(state):
    return "topic concept nested" + str(state)

#stateHeadDict={1: "h2",
#               2: 'h3',
#               3: 'h3',
#               4: 'h3'}

def getHeadNameByState(state):
    if state==1:
        return "h2"
    else:
        return "h3"


def getHeadClassByState(state):
    if state ==1:
        return "title topictitle1"
    else:
        return "title topictitle2"
    
#stateHeadClassDict={1: "title topictitle1",
#                    2: "title topictitle2",
#                    3: "title topictitle2",
#                    4: "title topictitle2"}




"""
navigation:
    <li>
       <div class="section-link" state="3">
        <a href="#50401315_pgfId-535633">
         1.1.2 Timeline View 1-2
        </a>
       </div>
      </li>
    
"""


def createATag(href, s):
    """ 
    example: <a href="#introduction"> 1. Introduction </a>
    """
    atag = soup.new_tag('a')
    atag['href'] = href
    atag.string = s
    return atag
        
def createDivTag(href, s, state, class_="section-link"):
    """ Example: 
    <div class="section-link" state="1">
    <a href="#introduction">
     1. Introduction
    </a>
   </div>
    """
    divtag = soup.new_tag('div')
    divtag['class'] = class_
    divtag['state'] = state
    atag = createATag(href, s)
    divtag.append(atag)
    return divtag
        
def createLiTag(href, s, state, class_="section-link"):
    """Example:
    <li>
     <div class="section-link" state="2">
      <a href="#from-graphics-processing-to-general-purpose-parallel-computing">
       1.1. From Graphics Processing to General Purpose Parallel Computing
      </a>
     </div>
    </li>
    """
    litag = soup.new_tag('li')
    divtag =  createDivTag(href, s, state, class_)
    litag.append(divtag)
    return litag

    # def createResizeNavTag():
    #     resizeTag = soup.new_tag('div')
    #     resizeTag['id'] = "resize-nav" 
    #     return resizeTag


def createNavTag(docname, titles):
    
    # first, rebuild navigator with nvida website template
    navtag = soup.new_tag('nav')
    navtag['id'] = "site-nav"
    
    # create the category div tag
    div1tag = createDivTag(href="http://{{host}}:{{port}}/{{docname}}/raw" , s = "Optimization Guide", state = 0, class_ = "category")
    navtag.append(div1tag)
    div2tag = createDivTag(href="http://{{host}}:{{port}}/{{docname}}/summary" , s = "Optimization Guide Summary", state = 0, class_ = "category")
    navtag.append(div2tag)

    # go through headlines to fill up ul1tag
    ultags = {}
    litags = {}
    old_state = 0
    
    for i in xrange(len(titles)):
        state = titles[i]["state"]
        litag = createLiTag(href= "#"+titles[i]["href"], s=titles[i]["title"], state=state)
        if old_state < state:
            # go deeper, need to create ul list
            ultag = soup.new_tag("ul")
            ultag.append(litag)
            ultags[state] = ultag
            litags[state] = litag
            if old_state>0:
                litags[old_state].append(ultag)
           
        else:
            ultags[state].append(litag)
            litags[state] = litag
            
        old_state = state
    navtag.append(ultags[1])
        
    return navtag

# content
"""<div class="topic concept nested2" id="50401315_pgfId-520762" xml:lang="en-US">
     <a name="50401315_pgfId-520762" shape="rect">
     </a>
     <h3 class="title topictitle2">
      <a href="http://developer.amd.com/tools-and-sdks/opencl-zone/amd-accelerated-parallel-processing-app-sdk/opencl-optimization-guide/#50401315_pgfId-520762" name="50401315_pgfId-520762" shape="rect">
       1.5.4 Mapping 1-20
      </a>
     </h3>
     <div class="body conbody">
      <ul class="ul">
       <li class="li">
        The host application can use clEnqueueMapBuffer / clEnqueueMapImage to obtain a pointer that can be used to access the memory object data.
       </li>
      </ul>
     </div>
     <div class="topic concept nested3" id="50401315_pgfId-503784" xml:lang="en-US">
"""
                   
def buildTopicContent(weblink, href, title, state, bodytag):
    """ Example:
    <div class="topic concept nested2" id="document-structure" xml:lang="en-US">
    <a name="document-structure" shape="rect">
    </a>
    <h3 class="title topictitle2">
     <a href="http://docs.nvidia.com/cuda/cuda-c-programming-guide/#document-structure" name="document-structure" shape="rect">
      1.4. Document Structure
     </a>
    </h3>
    ......
    </div>
    """
    # add head title
    divtag = soup.new_tag("div")
    divtag['class']= getDivClassByState(state)
    divtag["xml:lang"] = "en-US"
    divtag['id'] = href
    
    #add super link from navigator
    newatag = soup.new_tag('a')
    newatag['name'] = href
    newatag['shape'] = 'rect'
    divtag.append(newatag)
    
    # add headline
    h2tag = soup.new_tag(getHeadNameByState(state))
    h2tag['class'] = getHeadClassByState(state)
    superatag = soup.new_tag('a')
    superatag['href'] = weblink+'#'+href
    superatag['name'] = href
    superatag['shape'] = "rect"
    superatag.string = title
    h2tag.append(superatag)
    divtag.append(h2tag) 
    
    # add content
    if bodytag:
        divtag.append(bodytag)
    return divtag


def buildBodyContent(body, isFiltered, keywords):
    """ Example:
    <div class="body conbody">
     <ul class="ul">
      <li class="li">
       Chapter Performance Guidelines gives some guidance on how to achieve maximum performance.
      </li>
     </ul>
    </div>
    """
    
    if isFiltered:
        sents, allsents, inSummary =  filter_text(body, keywords)
    else:
        sents = sent_tokenize(body)

    divtag = soup.new_tag('div')
    divtag['class']="body conbody"
    
    ultag=soup.new_tag('ul')
    ultag['class'] = 'ul'
    for sent in sents:
        litag = soup.new_tag('li')
        litag['class'] = 'li'
        litag.string = sent
        ultag.append(litag)
    divtag.append(ultag)
    return divtag, len(sents)



def createContentTag(weblink, titles, isFiltered, keywords):
    contentTag = soup.new_tag('div')
    contentTag['id'] = "contents-container"
    articleHtml = soup.new_tag('article')
    articleHtml['id']= "contents"
    contentTag.append(articleHtml)
    
    totalSentsNumber = 0
    divtags = {}
    for item in titles:
        state = item['state']
        body = item['body']

        if len(body):
            bodytag, sentsN = buildBodyContent(body, isFiltered, keywords)
            totalSentsNumber += sentsN
        else:
            bodytag = None
        
        divtag = buildTopicContent(weblink=weblink, href=item['href'], 
                                    title=item['title'], state=state, bodytag=bodytag)
        if state ==1:
            articleHtml.append(divtag)
            divtags[state] = divtag
        else:
            divtags[state-1].append(divtag)
            divtags[state] = divtag
    return contentTag, totalSentsNumber
    
        
        

def build(docname, weblink, content=None, keywords=None, template_dir=None):
    """Save two HTML templates: summary.html, raw.html, into template_dir.
      Args:
        docname: The name of documentation, e.g. cuda, opencl.
        weblink: The link for the docname
        content: a content dictionary extracted with a parser 
        keywords: the set of words used to filter content 
        template_dir: the directory to save the HTML templates
      Returns:
        
      """
    if content==None:
    	raise ValueError('contents are None!' ) 
    if keywords==None:
        raise ValueError('keywords are None!' ) 
    if template_dir==None:
    	raise ValueError('template_dir is None!' ) 
    
    # print "save html to dir: ", template_dir
    check_directory(template_dir)
    
    navTag = createNavTag(docname, content)
    for isFiltered in [True, False]:

        contentTag, totalSentsNumber = createContentTag(weblink, content, isFiltered, keywords)
        # SentFilter will change the CWD to practnlptools. Need to change it back. 
        
        # save files
        if isFiltered:
            tosavename = os.path.join(template_dir, SUMMARY_HTML)
            print "After filtered, sents # = %d" %(totalSentsNumber)
        else:
            print "No filter, sents # = %d" %(totalSentsNumber)
            tosavename = os.path.join(template_dir, RAW_HTML)
        
        print "save as: ", tosavename
        
        with open(tosavename, 'w') as f:
            f.write("{% extends \""+docname+"/base.html\" %} \n ")
            f.write("{% block sitenav %}\n" + navTag.prettify('utf-8') +  "\n {% endblock %} \n")
            f.write("{% block content %}\n" + contentTag.prettify('utf-8')+ '\n {% endblock %} \n')   


            
            


        
