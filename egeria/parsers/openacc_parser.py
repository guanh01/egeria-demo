# openacc parser 

import re
from bs4 import BeautifulSoup
from egeria.helper import decode_ascii, decode_utf8, get_script_path
from pprint import pprint 

def clearTags(htmltext):
    # remove title
    # tags = htmltext.find_all(re.compile(r'h\d'))
    # for tag in tags:
    #     tag.clear()
        
    # remove other tag names with certain classes
    # tagClasses = ['p6 ft9', 'table','code']
    # for tagClass in tagClasses:
    #     codeTags = htmltext.find_all(class_=tagClass)
    #     for codeTag in codeTags:
    #         codeTag.clear()
    
    # remove other tag names with vertain tag names        
    tagNames = ['table', 'img']
    for tagName in tagNames:
        codeTags = htmltext.find_all(tagName)
        for tag in codeTags:
            tag.clear()

    # remove all the Figure title
    ps = htmltext.find_all('p')
    substring = "Figure"
    for p in ps:
    	# print p 
    	if substring == getText(p)[:len(substring)]:
    		p.clear() 
    return htmltext

# get text data in unicode format, get_text() return unicode string
def getText(htmltext):
    text = htmltext.get_text().strip()
    text = re.sub("\s+", " ", text)
    return text

def cleanTitle(title):
	return re.sub(r'\.', '', title).strip()

# extract all the navigation ref
def extractTitles(soupRaw):
    titles = []
    page1 = soupRaw.find('table', class_='t0')
    page2 = soupRaw.find('table', class_='t1')

    for child in  page1.contents+page2.contents:
    	if child.name!='tr':
    		continue
    	tds = child.find_all('td')
    	num_string = getText(tds[0])
    	title = cleanTitle(getText(tds[1]))
    	atag = child.find('a')
    	if atag:
    		href = atag['href'].split('#')[-1]
    	else:
    		continue   
    	if len(num_string)>0:
    		state = 1 # if it contains a number before the title, then it is the h1
    		title = num_string+' '+title
    	else: 
    		state = 2 
    	if "References" in title:
    		continue 
    	titles.append({'href': href, 'title': title, 'state': state})
    # pprint(titles)
    return titles

def clean_num_from_title(title):
	try:
		int(title[0])
	except:
		return title
	return title[1:].strip()

# secure title for pattern match 
def secure_title(title):
	title = re.sub('\?', "\\?", title)
	return title  

def extractContents(titles, text):
    for i in xrange(len(titles)):
        title = titles[i]['title']
        title = secure_title(clean_num_from_title(title))
        patterni = re.compile(">"+title+"</P>")
        resi= patterni.search(text)
        # print title, re.findall(">"+title+"</P>", text)
        if not resi:
            raise  ValueError("Error! Cannot find hrefi: "+hrefi)
        start = resi.end()
        # print title, resi, start 
        if i<len(titles)-1:
            titlej = secure_title(clean_num_from_title(titles[i+1]['title']))
        else:
            titlej = "Appendix A"
            
        patternj = re.compile(">"+titlej+"</P>")
        resj = patternj.search(text)#"<P>What is OpenACC?</P>")
        end = resj.start()
        # print titlej, resj, end  #re.findall(">"+titlej+"</P>", text)
        if start>=end:
            raise ValueError('start larger than end:', start, end)
        content = BeautifulSoup(text[start:end], 'lxml')     
        body = getText(clearTags(content))
        # print 'body', len(body), '\n'
        # if len(body)==4240:
        #     print 'body', body 
        # if len(body)==0:
        #     print 'text[start:end]:', text[start:end] 
        #     print 'content', content 
        #     print 'clearTags(content):', clearTags(content) 
        # newbody = cleanTitleFromBody(body, title)
        # if 'Accelerating an Application with OpenACC' in title:
        #     print 'body:', body
        titles[i]["body"] = replaceCharactersFromBody(body)
    return 

w2w={u'di\ufb00ering': u'differing',
		u'\ufb01rst': u'first',
		u'signi\ufb01cant': u'significant',
		u'di\ufb00erent': u'different',
		u'it\u2019s':u'it is',
		u'trade-o\ufb00': u'trade-off',
		u'\ufb01ts': u'fits',
		u'bene\ufb01cial': u'beneficial',
		u'\ufb01': u'fi',
		u'\ufb00': u'ff',
		u'di\ufb03culty': u'difficulty',
		u'\ufb03': u'ffi',
		u'\ufb04': u'ffl',
		u'\u2019': u'\'',
		u'--> ': u'',
		u'\u2022': u''
	}


def replaceCharactersFromBody(body):
	for key, value in w2w.iteritems():
		body = re.sub(key, value, body)
	return body 
        
            
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
                

def parse(filename):
    
    text = decode_utf8(open(filename, 'r').read())
    soupRaw = BeautifulSoup(text,"lxml")
    
    titles =  extractTitles(soupRaw) 
    extractContents(titles, text)
   	
    # print "titles length: ", len(titles)  
    # pprint(titles[10:20])
    return titles     


if __name__=='__main__':
	print ""
    