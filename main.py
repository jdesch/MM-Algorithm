#!/usr/bin/env python
# encoding: utf-8
"""
Main.py

Created by Justin Deschenes on 2011-04-26.
Copyright (c) 2011 . All rights reserved.
"""
import nltk
import random
import sys

from nltk.corpus import senseval

from memory import Memory

def chunk(l, n):
    for i in xrange(0, len(l), n):
           yield l[i:i+n]

def split_set2(num_split, instance_set):
    step = len(instance_set) / num_split
    cpy = [i for i in instance_set]
    random.shuffle(cpy)
    ret = list(chunk(cpy, step))
    return ret

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
    results = []
    mem = Memory()
    for i in range(test_iter):
        print "iteration %d ..." % (i + 1)
        ini_set = split_set2(folds, senseval.instances()[0:])
        for j in range(folds):
            print"...fold %d ..." % (j + 1)
            sets = partition_set(training_folds, ini_set, j)
            print "-$$Train time$$-"
            mem.train(sets[0])
            print "-$$results time$$-"
            results.append(mem.test(sets[1]))
    return results

def main(argv):
    iter = 1 if len(argv) == 0 else int(argv[0])
    results = test(iter, 5, 4)
    print "%3.1f %% accuracy" %( sum(results) / len(results) * 100)
    
def test_main():
    mem = Memory()
    print "loading data_set"
    ini_set = split_set2(5, senseval.instances()[0:10000])
    data_set = partition_set(4, ini_set, 0)
    #Serializer.save("/tmp/portioned_data", data_set)
    #data_set = Serializer.load("/tmp/portioned_data")
    print "training data"
    mem.train(data_set[0])
    #print "saving data"
    #mem.save_values("/tmp/mem_internals")
    #mem.load_values("/tmp/mem_internals")
    print "------*********testing**********------"
    results = mem.test(data_set[1])
    print "%3.1f %% accuracy" %(sum(results)/len(results) * 100)
    
if __name__ == "__main__":
    from utils.serializer import Serializer
    #test_main()
    main(sys.argv[1:])