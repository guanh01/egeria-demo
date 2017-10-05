#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 29 12:38:14 2017
set up 
@author: huiguan
"""


import os
import sys
sys.path.insert(0, './egeria')

from egeria import build_html, build_model, build_index, settings 
from egeria.parsers import parser_factory  
from egeria.keywords import keywords_factory  
from egeria.helper import get_script_path, check_directory
from config import doc2info  

script_path = get_script_path()
docs = sorted(doc2info.keys())
print "Setup for docs:", docs

# docs= ['cuda', 'opencl']

templates_dir = os.path.join(script_path, "templates")
models_dir = os.path.join(script_path, "models")

for docname in docs:
	
	print '---------------------'
	print "Setup for:", docname
	template_dir = os.path.join(templates_dir, docname)
	check_directory(template_dir)

	if not os.path.isfile(os.path.join(template_dir, settings.SUMMARY_HTML)):
		parse_fn = parser_factory.get_parse_fn(docname)

		doc_path = os.path.join(script_path, 'docs/'+ doc2info[docname]['filename'])
		if not os.path.isfile(doc_path):
			raise IOError('The documentation to be parsed does not exist:'+ doc_path)

		content = parse_fn(doc_path)
		build_html.build(docname=docname, 
						weblink=doc2info[docname]['weblink'], 
						content=content, 
						keywords = keywords_factory.get_keywords(docname),
						template_dir=template_dir)
	else:
	    print "Template already exist for", docname

	# print "Build dictionary and models. "
	model_dir = os.path.join(models_dir, docname)
	check_directory(model_dir)

	if not os.path.isfile(os.path.join(model_dir, settings.MODEL_FILE)):
	    build_model.build(template_dir, model_dir)
	else:
	    print "Model already exist for", docname 

	# print 'Build similarity index'
	if not os.path.isfile(os.path.join(model_dir, settings.INDEX_FILE)):
	    build_index.build(template_dir, model_dir)
	else:
	    print "Index already exist for", docname 

