# -*- coding: utf-8 -*-
"""
Created on Mon Sep 26 11:11:00 2016

read nvvp report and identify performance issue

issues format:

[
{'title': title, 'description':***, 'optimization': ***, 'section':***}
]

@author: huiguan
"""

#import PyPDF2
import textract, os, re

class ReadNvvpReport(object):
    def __init__(self):
        self.FSS = 'FirstStepState'
        self.LS = 'LatencyState'
        self.CS = 'ComputeState'
        self.MS = 'MemoryState'
        
        self.error_pattern = "Unfortunately,\s+the\s+device\s+executing\s+this\s+kernel\s+can\s+not\s+provide\s+the\s+profile\s+data\s+needed\s+for\s+this\s+analysis"
        
        self.stateDict = {self.FSS: 'Compute, Bandwidth, or Latency Bound',
                    self.LS: 'Instruction and Memory Latency',
                    self.CS: 'Compute Resources',
                    self.MS: 'Memory Bandwidth'}

    # identify the content under different topic
    def identifyContent(self, text):
        lines = text.split('\n')
        state = None
        content = ''
        data = []
        for idx in xrange(len(lines)):
            line = lines[idx].strip()
        
            if re.match(r'\d\.\s+Compute,\s+Bandwidth,\s+or\s+Latency\s+Bound', line):
                # in compute bandwidth or latency bound
                #print line
                state = self.FSS
                content = ''
                
            if re.match(r'\d\.\s+Instruction\s+and\s+Memory\s+Latency', line):
                #print line
                data.append((state, content.strip()))
                state = self.LS
                content = ''
                
            if re.match(r'\d\.\s+Compute\s+Resources', line):
                #print line
                data.append((state, content.strip()))
                state = self.CS
                content = ''
            
            if re.match(r'\d\.\s+Memory\s+Bandwidth', line):
                #print line
                data.append((state, content.strip()))
                state = self.MS
                content = ''
            
            if state==None:
                continue
            else:
                if line.isdigit():
                    continue
                content +=line+'\n'   # collect the content for a specic topic
                
        if len(content):
            data.append((state, content)) # capture the final state  
        return data

    def extractPerformanceIssues(self, data):
        Issues = []
        for key, value in data:
            if re.search(self.error_pattern, value):
                #print "No info for: %s" %(key)
                continue
            else:
                # identify content for each subsection excluding the first state
                #print "Collect info for: %s" %(key)
                subIssues = []
                content=''
                section = value[0] # section number, such as 1,2,3,4
                state = None
                lines = value.split('\n')
                for line in lines:
                    num = re.match(section+r'\.(\d)\.\s+', line) # find out the subsection title
                    if num:
                        number = num.groups()[0]
                        if int(number)>1:
                            # already not the first subsection
                            subIssues.append((state, content)) # previous subsection finished, collect content
                        content = ''
                        state = line.strip()
                        continue
                    if state:
                        content+=line.strip()+'\n'
                subIssues.append((state, content))
                Issues.append((key, subIssues))
        return Issues    


    def cleanContent(self, text):
        text = re.sub('\n', ' ', text.strip())
        text = re.sub('\(cid:9\)','', text)
        return text
        
        
    def extractRealIssues(self, Issues):
        realIssues = []
        for section in Issues: # section = (key, subIssues)
            for subsection in section[1]: # subsection = (key, subsectionIssues)
                if "Optimization:" not in subsection[1]:
                    # not a real issue
                    continue
                issueDict = {}
                issueDict['title'] = subsection[0]
                content = subsection[1].split('Optimization:')
                issueDict['description'] = self.cleanContent(content[0])
                issueDict['optimization'] = self.cleanContent(content[1])
                #issueDict['section'] = self.stateDict[section[0]]
                #print "code problem title: %s" %(subsection[0])
                realIssues.append(issueDict)
        return realIssues


    def report2issues(self, dirname, filename):    
        text = textract.process(os.path.join(dirname, filename),method='pdfminer')
        
        #print "---------------------------------"
        #print 'Identify different topics: %s \n' %(filename)
        
        data = self.identifyContent(text)
        
        # identify the issue description for subsections under a topic
        #print "---------------------"
        #print " Extract performance issue description: \n"
        
        Issues = self.extractPerformanceIssues(data)
        
        
        #print "---------------------"
        #print " Collect real performance issues: \n"
        
        # from issue description to performance issue: optimization methods
        
        realIssues = self.extractRealIssues(Issues)
        return realIssues




                
              
        




 
