#!/usr/bin/env python
# encoding: utf-8
"""
graph.py

Created by Justin Deschenes on 2011-05-28.
Copyright (c) 2011 . All rights reserved.
"""

class Node(object):
    def __str__(self):
        return "word: %s \t neighbors: %i \t seen: %i" %(self.word, len(self.neighbors), self.seen)
        
    def __init__(self, word):
        self.word = word
        self.neighbors = []
        self.seen = 1
        
    def __getstate__(self):
        tmp = self.__dict__.copy()
        ids = [neighbor.word for neighbor in tmp["neighbors"]]
        tmp["ids"] = ids
        del tmp["neighbors"]
        return tmp
        
    def __setstate__(self, state):
        self.__dict__ = state
        
    def add_neighbor(self, neighbor):
        if isinstance(neighbor, Node) and neighbor not in self.neighbors:
            self.neighbors.append(neighbor)
            neighbor.neighbors.append(self)
            return True
        return False
        
    def remove_neighbor(self, neighbor):
        if isinstance (neighbor, Node) and neighbor in self.neighbors:
            self.neighbors.remove(neighbor)
            neighbor.neighbors.remove(self)
            return True
        return False
    

class Graph(object):
    def __init__(self):
        self.nodes = {}
        self.edges = {}
    
    @staticmethod
    def setup_saved_graph(graph):
        tmpgraph = Graph()
        tmpgraph.edges = graph.edges
        for word, node in graph.nodes.iteritems():
            node.__dict__["neighbors"] = [graph.nodes[ids] for ids in node.ids]
            del node.__dict__["ids"]
        tmpgraph.nodes = graph.nodes
        return tmpgraph
    
    def update_edges(self, n1, n2, val=None):
        if val:
            value = val
        else:
            value = 1
            
        if self.edges.get(n1,n2):
            self.edges[(n1, n2)] = self.edges.get((n1, n2), 0) + value
        else:
            self.edges[(n2, n1)] = self.edges.get((n2, n1), 0) + value
    
    def get_edge_val(self, word1, word2):
        if word1 in self.nodes and word2 in self.nodes and not isinstance(word1, Node) and not isinstance(word2, Node):
            if (self.nodes[word1], self.nodes[word2]) in self.edges:
                return self.edges[(self.nodes[word1], self.nodes[word2])]
            elif(self.nodes[word2], self.nodes[word1]) in self.edges:
                return self.edges[(self.nodes[word2], self.nodes[word1])]
            else:
                return 0
        elif isinstance(word1, Node) and isinstance(word2, Node):
            if(word1, word2) in self.edges:
                return self.edges[(word1, word2)]
            elif(word2, word1) in self.edges:
                return self.edges[(word2, word1)]
            else:
                return 0
        else:
            return None
    
    def add_node(self, word):
        if word in self.nodes:
            self.nodes[word].seen += 1
        else:
            self.nodes[word] = Node(word)
           
        return self.nodes[word]
        
    def get_edge(self, n1, n2):
        if (n1, n2) in self.edges:
            return self.edges[n1, n2]
        elif (n2, n1) in self.edges:
            return self.edges[n2, n1]
        else:
            print "error no edge found for %s, %s" %(n1, n2)
    
    def add_neighbors(self, node, neighbors):
        if not isinstance(neighbors, list):
                node.add_neighbor(neighbors)
                self.update_edges(node, neighbors)
        else:
            for n in neighbors:
                self.update_edges(node, n)
                node.add_neighbor(n)
    
    def set_neighbor_network(self, network, target):
        nodes = [] 
        for i,n in enumerate(network):
            if i != target[1]:
                nodes.append(self.add_node(n[0]))
            else:
                word = "%s#%s" %(target[0][0], target[2][0])
                nodes.append(self.add_node(word))
        #print "node length %i" %len(nodes)
        for i,node in enumerate(nodes[0:len(nodes)-1]):
            self.add_neighbors(node, nodes[i+1:])
            #print "iter %i, node %s" %(i, node)
    
    def get_neighbors(self, node):
        if isinstance(node, Node):
            retlist = []
            for n in node.neighbors:
                retlist.append((self.get_edge(node,n), n))
            #print "%s" %(len(retlist))
            retlist.reverse()
            return retlist 
