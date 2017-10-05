
import os 
from gensim import models, similarities, corpora
from bs4 import BeautifulSoup
from egeria.helper import docs2vecs, load_pickle , save_pickle
from egeria.settings import SUMMARY_HTML , INDEX_FILE 

def build(template_dir, model_dir):
    """Save similarity index built based on sourcefile into model_dir.
     Args:
       sourcefile: html sourcefile path
       model_dir: the directory to save the index
    """
    soup = BeautifulSoup(open(os.path.join(template_dir, SUMMARY_HTML)), "lxml")
    dictionary = load_pickle(dirname = model_dir, filename='dictionary.pckl')  
    themodel = load_pickle(dirname= model_dir, filename='model.pckl')
    htmltext = soup.find('article') # id="contents"
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
    sentsVec = docs2vecs(sents, dictionary, themodel)
    index = similarities.MatrixSimilarity(sentsVec, num_features = len(dictionary))
    save_pickle(index, model_dir, filename=INDEX_FILE)