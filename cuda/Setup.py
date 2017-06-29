#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 29 12:38:14 2017
set up 
@author: huiguan
"""


import os
import sys
sys.path.insert(0, '../utils')

from Helper import get_script_path
from Parser import parser
from Config import guidename

print "Build templates: index.html, rawIndex.html"
templates_dir = os.path.join(get_script_path(), "templates")
if not os.path.isfile(os.path.join(templates_dir, "index.html")):
	from BuildIndexHtml import buildIndexHtml
	buildIndexHtml(parser(guidename), templates_dir)
else:
    print "html files already exist. Skip buildIndexHtml."

print "Build dictionary and models. "
from Config import model_filename
models_dir = os.path.join(get_script_path(), "models")
if not os.path.isfile(os.path.join(models_dir, model_filename)):
    from BuildDictAndModels import buildDictAndModels
    buildDictAndModels(templates_dir, models_dir)
else:
    print "models already exit. Skip buildDictAndModels. "

