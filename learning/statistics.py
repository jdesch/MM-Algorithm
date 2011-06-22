#!/usr/bin/env python
# encoding: utf-8
"""
statistic.py

Created by Justin Deschenes on 2011-05-28.
Copyright (c) 2011 . All rights reserved.
"""

import random

from structures.word import Word, Disambiguation
from structures.leds import LEDS

class Statistics(object):
    def __init__(self):
        self.words = {}
        self.targets = 0
        self.total_words = 0
    
    def load_words(self, words):
        self.words = words
    
    def train_words(self, wordlist, target):
        for i,sets in enumerate(wordlist):      #for every sentence in wordlist
            for j,word in enumerate(sets):      #for every word in sentence
                self.total_words += len(sets)
                if j == target[i][1]:           #if instance is target word
                    w = "%s" %(target[i][0][0]) #get target value
                    if self.words.get(w):       #if the word exists
                        self.words[w].update(target[i][2][0])  #update its disambiguation
                    else:
                        self.targets += 1
                        self.words[w] = Word(w, target[i][2][0]) #otherwise create it, with its disambiguation
                    self.words[w].dict["disambiguations"][target[i][2][0]].add_seen_words([w[0] for w in sets]) #update words it has seen
                else:                           #the word is not a target
                    if self.words.get(word[0]):    # if it exists
                        self.words[word[0]].update()  #update it
                    else:
                        self.words[word[0]] = Word(word[0])  #otherwise create it
                    self.words[word[0]].trained()
    
    def vote(self, words, target, leds):
        ret = (0.0, None)
        t = self.words[target]
        values = []
        total = 0.0
        for dis in t.dict["disambiguations"]:
            dis_sum = 0.0
            for w in words:
                if w in self.words and w in t.dict["disambiguations"][dis].seen:
                    freq_denom = float(t.dict["disambiguations"][dis].seen[w])
                    freq_quot = float( t.dict["disambiguations"][dis].dict["total"])
                    accu_denom = float(self.words[w].dict["correct"])
                    accu_quot = float(self.words[w].dict["total"])
                    dis_sum += (freq_denom * accu_denom)/(freq_quot * freq_denom)
            values.append((dis_sum, dis))
            total += dis_sum
            
        for (val,dis) in values:
            if val > ret[0]:
                ret = (val/total, dis)
        leds.statistic_guess(ret[1])
        return ret
        
    def best_guess(self, target, leds):
        ret = (0.0, None)
        t = self.words[target]
        total = 0
        for dis in t.dict["disambiguations"]:
            val = t.dict["disambiguations"][dis].dict["total"]
            total += val
            if val > ret[0]:
                ret = (val, dis)
        ret = (float(ret[0])/float(total), ret[1])
        leds.statistic_guess(ret[1])
        return ret
    
    def get_best_words(self, target, wordlist, meta_values):
        size = 0
        try:
            size = meta_values["important_words"]["value"]
        except Exception, e:
            size = 4
        val = [self.get_word_importance(target, t) for t in wordlist if t != target]
        val = zip(val, wordlist)
        val.sort(reverse=True)
        val = list(set(val))
        return [word for (value, word) in val[0:size]]
    
    def get_word_importance(self, target, word):
        ret = 0.0
        t = self.words[target]
        if self.words.get(word):
            seen_denom = sum([t.dict["disambiguations"][dis].seen.get(word, 0) for dis in t.dict["disambiguations"]])
            seen_quot = sum([t.dict["disambiguations"][dis].dict["total"] for dis in t.dict["disambiguations"]])
            ret = float(seen_denom) / float(seen_quot)
        return ret
    
    def get_generic_word_importance(self, word):
       return (word.dict["correct"] / word.dict["total"])
    

    