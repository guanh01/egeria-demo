#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 28 13:46:30 2017
congiguration
@author: huiguan
"""


port = '5000'
host = '152.14.93.113'


similarity_threshold = 0.15


doc2info={
      'cuda': {
            "filename": "Programming Guide __ CUDA Toolkit Documentation.html",
            'weblink': "http://docs.nvidia.com/cuda/cuda-c-programming-guide/"},
      'opencl': {
            "filename": "OpenCL Optimization Guide - AMD.html",
            'weblink': "http://developer.amd.com/tools-and-sdks/opencl-zone/amd-accelerated-parallel-processing-app-sdk/opencl-optimization-guide/"},
      'openacc': {
            'filename': 'openacc_light.htm',
            'weblink': 'http://{{host}}:{{port}}/openacc/guide'
            }}



