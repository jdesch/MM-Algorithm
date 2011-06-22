#!/usr/bin/env python
# encoding: utf-8
"""
leds.py

Created by Justin Deschenes on 2011-05-28.
Copyright (c) 2011 . All rights reserved.
"""

class LEDS(object):
    def __init__(self):
        self._words = []
        self.success_info = {}
        self.node_selected_graph = None
    
    def add_discovered_words(self, words):
        self._words.append(words)
    
    def statistic_guess(self, guess):
        self.success_info["stats_guess"] = guess
    
    def graph_guess(self, guess):
        self.success_info["graph_guess"] = guess
    
    def completed(self, actual_sense, selected_sense):
        self.success_info["actual_val"] = actual_sense
        self.success_info["selected_val"] = selected_sense