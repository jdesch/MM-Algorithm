#!/usr/bin/env python
# encoding: utf-8
"""
word.py

Created by Justin Deschenes on 2011-05-28.
Copyright (c) 2011 . All rights reserved.
"""

class Disambiguation(object):
    def __str__(self):
        return "%s- %s, %s, %s" %(self.dis, self.dict["guessed"], self.dict["correct"], self.dict["total"])
    
    def __init__(self, disambiguation):
        self.dis = disambiguation
        self.dict = {"guessed":0, "correct":0, "total":1, "total_words":0}
        self.seen = {}
    
    def visited(self):
        self.dict["total"] += 1
        
    def trained(self):
        self.dict["guessed"] += 1
        self.dict["correct"] += 1
    
    def completed(self, correct):
        self.dict["guessed"] = self.dict.get("guessed", 0) + 1
        if correct:
            self.dict["correct"] = self.dict.get("correct", 0) + 1
            
    def add_seen_words(self, words):
        self.dict["total_words"] += len(words)
        for w in words:
            self.seen[w] = self.seen.get(w, 0) + 1
            
    def get_seen_words(self):
        return ",".join(["%s:%s" %(k,v) for k,v in self.seen.iteritems()])
            
    def seen(self, word):
        if self.seen.get(word):
            return self.seen[word]
        else:
            return 0
    

class Word(object):
    def __init__(self, word, dis=None):
        self.dict = {"word":word, "total":1, "completions":0, "correct":0, "disambiguations":{}}
        if dis:
            self.dict["disambiguations"][dis] = Disambiguation(dis)
            
    def trained(self):
        self.dict["correct"] += 1
        self.dict["completions"] += 1
    
    def update(self, dis=None):
        self.dict["total"] += 1
        if dis:
            if self.dict["disambiguations"].get(dis):
                self.dict["disambiguations"][dis].visited()
            else:
                self.dict["disambiguations"][dis] = Disambiguation(dis)
    
    def add_info(self, correct, dis=None):
        self.dict["completions"] += 1
        if correct:
            self.dict["correct"] += 1
        if dis:
            if dis not in self.dict["disambiguations"]:
                self.dict["disambiguations"][dis] = Disambiguation(dis)
            self.dict["disambiguations"][dis].completed(correct)
