#!/usr/bin/env python
# encoding: utf-8
"""
connective.py

Created by Justin Deschenes on 2011-05-28.
Copyright (c) 2011 . All rights reserved.
"""
from utils.wordhandling import Handler
from structures.graph import Graph, Node
from structures.leds import LEDS

class Connective:
    def __init__(self):
        self.graph = Graph()
    
    def load_graph(self, graph):
        self.graph = graph
    
    def train_network(self, wordlist, targetlist):
        if len(wordlist) != len(targetlist):
            print "Error creating the graph"
        else:
            for i in range(len(wordlist)):
                self.graph.set_neighbor_network(wordlist[i],targetlist[i])
        
    def vote(self, words, target, meta_dict, leds):
        vote = {}
        current = words
        next = []
        depth = 0
        nodes = {}
        
        while len(vote) < len(words) and depth < meta_dict["graph_depth"]["value"]:
            for w in current:
                if self.graph.nodes.get(w):
                    node = self.graph.nodes[w]
                    neighbors = self.graph.get_neighbors(node)
                    solved = False
                    if neighbors:
                        for n in neighbors:
                            if "#" in n[1].word:
                                if Handler.compare_target(target, n[1].word):
                                    solved = True
                                    val = n[1].word.split('#')[-1]
                                    vote[val] = vote.get(val, 0) + 1
                                    nodes[val] = n[1]
                                    break
                        if not solved:
                            next.append(neighbors[0])
            depth += 1
            current = next
            next = []
            leds.add_discovered_words(current)
            
        highest = 0
        sense = None
        for key, val in vote.items():
            if val > highest:
                highest = val
                sense = key
        ret = (float(highest)/float(len(words)), sense)
        if ret[1]:
            leds.node_selected_graph = nodes[ret[1]]
            leds.graph_guess(ret)
        else:
            leds.node_selected_graph = None
            leds.graph_guess(None)
        return ret
    

