#!/usr/bin/env python
# encoding: utf-8
"""
comparison.py

Created by Justin Deschenes on 2011-05-28.
Copyright (c) 2011 . All rights reserved.
"""

from nltk.stem.wordnet import WordNetLemmatizer as wnl
from nltk.corpus import stopwords

from string import punctuation

class Handler(object):
    def __init__(self, dataset=None):
        if dataset:
            self.dataset = dataset
        self.pos_lookup = {"JJ":"a", "JJR":"a", "JJS":"a", "NN":"n", "NNS":"n", "NNP":"n", "NNPS":"n",
                                   "VB":"v", "VBD":"v", "VBG":"v", "VBN":"v", "VBP":"v", "VBZ":"v"}
        self.artifacts = ["''", "``", "'", ")"]
        
    @staticmethod
    def compare_target(target, word):
        tar = target.split("#")[-1].rstrip('0123456789')
        if tar.upper() in word.upper():
            return True
        return False
        
    def get_word_and_target_list(self, set):
        wordlist = []
        targetlist = []
        stopset = stopwords.words('english')
        stopset.extend(self.artifacts)
        wordnet = wnl()
        
        for i,inst in enumerate(set):
            wordlist.append([])
            tmplist = [w for w in inst.context if isinstance(w, tuple) and w[1] not in punctuation and w[0] not in stopset]
            newpos = tmplist.index(inst.context[inst.position])
            for word in tmplist:
                if self.pos_lookup.get(word[1]):
                    wordlist[i].append((wordnet.lemmatize(word[0], self.pos_lookup[word[1]]), word[1]))
                else:
                    wordlist[i].append(word)
            targetlist.append((tmplist[newpos], newpos, inst.senses))
        return (wordlist, targetlist)
        
    

