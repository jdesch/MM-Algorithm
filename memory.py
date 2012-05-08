#!/usr/bin/env python
# encoding: utf-8
"""
Memory.py

Created by Justin Deschenes on 2011-04-18.
Copyright (c) 2011 . All rights reserved.
"""

from nltk.corpus import senseval

from utils.serializer import Serializer
from utils.wordhandling import Handler
from structures.leds import LEDS
from structures.graph import Graph, Node
from structures.word import Word, Disambiguation
from learning.statistics import Statistics
from learning.connective import Connective
from learning.meta import Meta

class Memory(object):
    def __init__(self, save_load=None):
        if not save_load:
            self.stats = Statistics()
            self.connect = Connective()
            self.meta = Meta()
            self.handler = Handler()
        else:
            self.save_location = save_load
            self.load_values()
    
    def __del__(self):
       try:
           self.save_values()
       except Exception, e:
           print "Memory Garbage Collected, no save on exit (no save location)"
    
    def load_values(self, loc=None):  #FIX THIS WITH NEW WAY OF LEARNING
        if loc:
            tmp_dict = Serializer.load(loc)
        else:
            tmp_dict = Serializer.load(self.save_location)
        
        self.graph = Graph.setup_saved_graph(tmp_dict["graph"])
        self.words = tmp_dict["words"]
        self.meta_values = tmp_dict["meta_values"]
        self.inner_stats = tmp_dict["inner_stats"]
    
    def save_values(self, loc=None):  #FIX WITH NEW WAY OF LEARNING
        tmp_dict = {"graph": self.graph, "words": self.words, "meta_values": self.meta_values, "inner_stats": self.inner_stats}
        if loc:
            Serializer.save(loc, tmp_dict)
        else:
            Serializer.save(self.save_location, tmp_dict)
    
    def train(self, set, from_scratch=True):
        if from_scratch:
            self.stats = Statistics()
            self.connect = Connective()
            self.save_location = None
            
        print "setting up instances"
        wordlist, target = self.handler.get_word_and_target_list(set)
        print "loading graph"
        self.connect.train_network(wordlist, target)
        print "loading words"
        self.stats.train_words(wordlist, target)
        print "optimizing mind"
        self.optimize(wordlist, target)
    
    def compose_answer(self, words, target, leds):
        if words:
            leds.add_discovered_words(words)
            graph_vote = self.connect.vote(words, target, self.meta.meta_values, leds)
            stat_vote = self.stats.vote2(words, target, leds)
            return self.meta.vote(graph_vote, stat_vote)
        else:
            return self.stats.best_guess(target, leds)
    
    def optimize(self, wordlist, target):
        for i in range(len(target)):
            leds = LEDS()
            words = self.stats.get_best_words(target[i][0][0], [w[0] for w in wordlist[i]], self.meta.meta_values)
            vote = self.compose_answer(words, target[i][0][0], leds)
            leds.completed(target[i][2], vote)
            print "\t\t actual val: %s" %(target[i][2])
            self.meta.learn(leds, self.connect.graph, self.stats.words)
        self.meta.optimize()
    
    def guess(self, wordlist, target_info):
        leds = LEDS()
        words = self.stats.get_best_words(target_info[0][0], [w[0] for w in wordlist], self.meta.meta_values)
        answer = self.compose_answer(words, target_info[0][0], leds)
        #print ("words = %s, answer= %s") %(", ".join(words), answer)
        return answer[1]
    
    def test(self, set):
        correct = 0
        wordlist, target = self.handler.get_word_and_target_list(set)
        correct_value = [t[2] for t in target]
        target_info = [(t[0], t[1]) for t in target]
        
        for i in range(len(wordlist)):
            guess = self.guess(wordlist[i], target_info[i])
            print "\t\t actual val: %s" %(correct_value[i][0])
            if guess == correct_value[i][0]:
                correct += 1
        print "test accuracy: %s" %(float(correct)/float(len(wordlist)))
        return float(correct)/float(len(wordlist))
    
