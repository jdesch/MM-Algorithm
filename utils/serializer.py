#!/usr/bin/env python
# encoding: utf-8
"""
serializer.py

Created by Justin Deschenes on 2011-01-25.
Copyright (c) 2011 . All rights reserved.
"""

import unittest
import cPickle as pickle
import os

class Serializer:
    @staticmethod
    def load(filename):
        try:
            f = open(filename, 'r')
            ret = pickle.load(f)
            f.close()
        except IOError as e:
            ret = False
            print e
        return ret
    
    @staticmethod
    def save(filename, obj):
        ret = True
        try:
            f = file(filename, 'w')
            pickle.dump(obj, f)
            f.close()
        except IOError as e:
            ret = False
            print e
        return ret
    
