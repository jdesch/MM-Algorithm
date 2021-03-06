#!/usr/bin/env python
# encoding: utf-8
"""
meta.py

Created by Justin Deschenes on 2011-05-28.
Copyright (c) 2011 . All rights reserved.
"""

import unittest
import random
from math import sqrt

from structures.leds import LEDS
from structures.graph import Graph, Node
from structures.word import Word, Disambiguation

class Meta:
    def __init__(self):
        self.inner_stats = {"total" : 0, "correct" : 1, "stats_correct" : 1,
                            "graph_correct" : 0, "last_update" : 0, "last_correct" : 0,
                             "last_value" : None, "old_values" : [] }
        self.meta_values = {"important_words": {"value":4, "step":1, "history":[]},
                            "graph_depth": {"value":3, "step":1, "history":[]},
                            "g_correct": {"value":3, "step": 1, "history":[]},
                            "g_incorrect": {"value":-1, "step": -1, "history": []},
                            "update_freq": {"value":300, "step": 100, "history":[]}}
    
    def load_inner_stats(self, stats):
        self.inner_stats = stats
    
    def load_meta_values(self, meta):
        self.meta_values = meta
    
    def stats_correct(self):
        return float(self.inner_stats["stats_correct"])/float(self.inner_stats["correct"])
    
    def graph_correct(self):
        return float(self.inner_stats["graph_correct"])/float(self.inner_stats["correct"])
    
    def vote(self, graph_vote, stat_vote):
        ret = None
        graph_val = float(graph_vote[0]) * self.graph_correct()
        stat_val = float(stat_vote[0]) * self.stats_correct()
        print "\t\t adjusted vote: graph: (%s,%3.1f), stat: (%s,%3.1f)" %(graph_vote[1], graph_val, stat_vote[1], stat_val)
        if graph_val > stat_val:
            ret = (graph_val, graph_vote[1])
        else:
            ret = (stat_val, stat_vote[1])
        return ret
    
    def learn(self, leds, graph_str, word_str):
        target = leds.node_selected_graph
        update_val = None
        
        if leds.success_info.get("stats_guess") and leds.success_info.get("actual_val"):
            stats_success = (leds.success_info["stats_guess"] == leds.success_info["actual_val"])
        else:
            stats_success = False
        
        if leds.success_info.get("graph_guess") and leds.success_info.get("actual_val"):
            if leds.success_info["graph_guess"] == leds.success_info["actual_val"]:
                update_val = self.meta_values["g_correct"]["value"]
                for words in leds._words:
                    for w in words:
                        node = graph_str.nodes[w]
                        graph_str.update_edges(node, target, update_val)
            else:
                update_val = self.meta_values["g_incorrect"]["value"]
                for words in leds._words:
                    for w in words:
                        if graph_str.nodes.get(w):
                            node = graph_str.nodes[w]
                            graph_str.update_edges(node, target, update_val)
        
        for words in word_str:
            for w in words:
                if word_str.get(w):
                    word = word_str[w]
                    word.add_info(stats_success)
        
        if target:
            target = word_str[target.word.split('#')[0]]
            target.add_info(stats_success, leds.success_info["actual_val"][0])
        
        self.inner_stats["total"] += 1
        if leds.success_info["actual_val"][0] == leds.success_info["selected_val"][1]:
            self.inner_stats["correct"] += 1
            if leds.success_info["actual_val"][0] == leds.success_info["stats_guess"]:
                self.inner_stats["stats_correct"] += 1
            if leds.success_info["actual_val"][0] == leds.success_info["graph_guess"][1]:
                self.inner_stats["graph_correct"] += 1
        
        self.optimize()
    
    def step_value(self, value, reverse = False):
        step = self.meta_values[value]["step"]
        current = self.meta_values[value]["value"]
        self.meta_values[value]["history"].append((current, (not reverse)))
        if not reverse:
            self.meta_values[value]["value"] = current + step
        else:
            self.meta_values[value]["value"] = current - step
    
    def get_current_correct(self):
        new_correct = float(self.inner_stats["correct"] - self.inner_stats["last_correct"])
        new_correct /= float(self.inner_stats["total"] - self.inner_stats["last_update"])
        return new_correct
    
    def get_current_std_dev(self):
        correct = 1.00 if self.get_current_correct() > 1.00 else self.get_current_correct()
        incorrect = 0.0 if (1.0 - correct) < 0.0 else (1.0 - correct)
        total = self.inner_stats["total"] - self.inner_stats["last_update"]
        return sqrt((correct*incorrect)/total)
    
    def performance_eval(self, metric_name):
        #print "evaluating performance..."
        ret_val = True
        old_correct, old_std_dev = self.inner_stats["old_values"][-1]
        new_correct = self.get_current_correct()
        print "#performance stats- instances- %s, new_correct %s, percentage %s, old_percentage %s, std_dev %s" %(self.meta_values["update_freq"]["value"], new_correct * self.meta_values["update_freq"]["value"], new_correct, old_correct, old_std_dev)
        print "#overall stats- total instances run %s, correct %s, graph correct %s, stats correct %s" %(self.inner_stats["total"], self.inner_stats["correct"], self.inner_stats["graph_correct"], self.inner_stats["stats_correct"])
        if new_correct > (old_correct + old_std_dev): #the change had a positive effect (std_dev's better then old)
            print "\t%s Improved, permanent change" %(metric_name)
            self.step_value(metric_name)
            ret_val = False
        elif new_correct < (old_correct - old_std_dev):
            print "\t%s Regressed, remove last change" %(metric_name)
            self.step_value(metric_name, reverse=True)
        print "======================="
        return ret_val
    
    def get_random_meta_value(self):
        values = [value for value in self.meta_values.keys()]
        ret = values[random.randrange(len(values))]
        return ret
    
    def optimize(self):
        new_value_required = True
        if self.meta_values["update_freq"]["value"] > (self.inner_stats["total"] - self.inner_stats["last_update"]):
            return
        else:
            #print "optimizing meta learning"
            if self.inner_stats["last_value"]: #if a value was worked on, evaluate it.
                new_value_required = self.performance_eval(self.inner_stats["last_value"])
            
            self.inner_stats["old_values"].append((self.get_current_correct(), self.get_current_std_dev()))
            self.inner_stats["last_update"] = self.inner_stats["total"]
            self.inner_stats["last_correct"] = self.inner_stats["correct"]
            
            val = self.inner_stats["last_value"] if not new_value_required else self.get_random_meta_value()
            self.inner_stats["last_value"] = val
            self.step_value(val)
            #print "updating value %s" %val
    


