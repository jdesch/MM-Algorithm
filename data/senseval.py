#!/usr/bin/env python
# encoding: utf-8
"""
senseval.py

This program runs the senseval-2 datasets through a most sensed training
method (randomized and cross validated), then returns the accuracy on the
test set.

Created by Justin Deschenes on 2011-01-25.
Copyright (c) 2011 . All rights reserved.
"""

import nltk
import random
import sys

def split_set(num_split, instance_set):
    import decimal as d
    import math
    n = len(instance_set)
    step = int(math.floor(d.Decimal(n) / d.Decimal(num_split)))
    left = n - (num_split * step)
    ret = []
    cpy = [i for i in instance_set]
    random.shuffle(cpy)
    for i in range(num_split):
        temp= []
        for j in range(i * step, (i + 1) * step):
            temp.append(cpy[j])
            if left > 0:
                print("adding value:", cpy[step * num_split + i])
                temp.append(cpy[step * num_split + i])
                left -= 1
        ret.append(temp)
    return ret    
    
def get_most_sensed_list(training_set):
     from nltk.corpus import senseval
     t = training_set
     d = {}
     ret = {}
     for i in range(len(t)):
             key = t[i].word
             val = t[i].senses
             if key in d:
                     if val in d[key]:
                             d[key][val] += 1
                     else:
                             d[key][val] = 1
             else:
                     d[key] = {}
                     d[key][val] = 1
     for k,v in d.iteritems():
             high = 0
             val = ""
             for k2,v2 in v.iteritems():
                     if v2 > high:
                             (high, val) = (v2, k2)
             ret[k] = val
     return ret
 
def most_sensed_checked(dict, work_set):
    n = len(work_set)
    correct = 0
    for i in range(n):
        if instance_check(work_set[i], dict[work_set[i].word]):
            correct += 1
    return (correct, n)
    
def instance_check(instance, guess):
    return (instance.senses == guess)
    
def partition_set(num_training, set, offset):
    ret = []
    temp = []
    last = 0
    for i in range (num_training):
        temp += set[(offset + i) % len(set)]
        last = i
    ret.append(temp)
    ret.append(set[(last + offset + 1) % len(set)])
    return ret
  
def test(test_iter, folds, training_folds):
    from nltk.corpus import senseval
    results = []
    for i in range(test_iter):
        print "iteration %d ..." % (i + 1)
        ini_set = split_set(folds, senseval.instances())
        for j in range(folds):
            print"...fold %d ..." % (j + 1)
            set = partition_set(training_folds, ini_set, j)
            trndict = get_most_sensed_list(set[0])
            results.append(most_sensed_checked(trndict, set[1]))
    return results

def main(argv):
    iter = 1 if len(argv) == 0 else int(argv[0])
    correct = 0.0
    total = 0.0
    results = test(iter, 5, 4)
    for r in results:
        correct += r[0]
        total += r[1]    
    print "accuracy for most sensed = %3.1f %% over %d attempts" % ((correct / total * 100), total)
    
if __name__ == "__main__":
    main(sys.argv[1:])