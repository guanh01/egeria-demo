# testQueryEngineHtml.py
from QueryEngineHtml import QueryEngineHtml
from bs4 import BeautifulSoup

queryEngine = QueryEngineHtml("../cuda/models/")

# build simIndex
source_file = "../cuda/templates/index.html"
soup = BeautifulSoup(open(source_file), "lxml")
htmltext = soup.find('article') # id="contents"
simIndex = queryEngine.buildSimIndex(htmltext)
print '#sents=', len(simIndex)

# an example query
query = 'memory'
issueDict = {'title': query}
queries = queryEngine.issues2queries(issues=[issueDict])
print "queries:", queries

# calculate similarity
indexes = queryEngine.getRetrievedSentsIndex(simIndex, issues=[issueDict], sim_thr=0.15)
queryEngine.traverseHtml(htmltext, indexes)

