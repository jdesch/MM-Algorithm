#! /usr/bin/env python
#  encoding: utf-8
"""
results.py

Created by Justin Deschenes on 2012-01-30.
Copyright (c) 2011 . All rights reserved.
"""
import argparse
import os.path
import pprint

sections = []
curr_obj = []
line_num = 0
test_started = 0
last_val = ""
last_state = ""

def isFloat(string):
	try:
		float(string)
		return True
	except ValueError:
		return False


def isNonFloatNum(string):
	try:
		int(string)
		return True
	except ValueError:
		return False


def parse_voting(line, instance):
	if instance == 0:
		return tuple(str(line[line.find('(') + 1: line.find(')')]).split())
	else:
		return tuple(str(line[line.rfind('(') + 1: line.rfind(')')]).split())


def process_lines(line):
	global sections
	global curr_obj
	global line_num
	global test_started
	global last_val
	global last_state  # to remove accidental doubles in data

	line_num += 1

	if '-$$Train' in line:
		curr_obj.append({"train": {}})
		last_val = "train"
		curr_obj[-1][last_val]["graph_vote"] = []
		curr_obj[-1][last_val]["stat_vote"] = []
		curr_obj[-1][last_val]["actual_val"] = []
	elif 'adjusted vote' in line:
		if last_state != 'adjusted vote':
			curr_obj[-1][last_val]["graph_vote"].append(parse_voting(line, 0))
			curr_obj[-1][last_val]["stat_vote"].append(parse_voting(line, 1))
		last_state = 'adjusted vote'	
	elif 'actual val' in line:
		if last_state != 'actual val':
			curr_obj[-1][last_val]["actual_val"].append(line.split()[-1])
		last_state = 'actual val'
	elif '-$$results' in line:
		test_started = line_num
		curr_obj[-1]["results"] = {}
		last_val = "results"
		curr_obj[-1][last_val]["graph_vote"] = []
		curr_obj[-1][last_val]["stat_vote"] = []
		curr_obj[-1][last_val]["actual_val"] = []
	elif 'test accuracy' in line:
		curr_obj[-1]["test_num"] = int((line_num - test_started) / 2)
		curr_obj[-1]["accuracy"] = float(line[ line.find(".") - 1 : ] )
		sections.append( curr_obj )
	elif line.endswith( "accuracy" ):
		sections.append( {"final":{ "accuracy" : float( line[ 0 : 4 ] )}} )


def get_correct_words( sections, instance="results", component="graph_vote" ):
	word_count = {}

	for obj in sections:
		if obj.has_key(instance):
			print "%s" %(len(obj[instance]["graph_vote"]))
			for i in xrange(len(obj[instance]["graph_vote"])):
				val = obj[instance]["actual_val"][i]
				if component == "graph_vote":
					inst = obj[instance]["graph_vote"][i][0]
					if val in inst and val not in obj[instance]["stat_vote"][i][0]:
						if word_count.get( getWord( inst ) ):
							word_count[ getWord( inst ) ][0] += 1
							if ( inst, obj[instance]["stat_vote"][i][0] ) not in word_count[ getWord( inst ) ][1]:
								word_count[ getWord( inst ) ][1].append( ( inst, obj[instance]["stat_vote"][i][0] ) )
						else:
							word_count[ getWord( inst ) ] = [ 1, [ ( inst, obj[instance]["stat_vote"][i][0] ) ] ]
	return word_count	


def get_results(sections):
	headings = ["test instances", "accuracy"]
	results = []

	for obj in sections:
		if obj.has_key("results"):
			for inst in obj:
				results.append([ obj["test_num"], obj["accuracy"] ])

	return (headings, results)

def get_biasness( sections, instance="train", component="graph_vote" ):
	values = []
	notComponent = "graph_vote" if component == "stat_vote" else  "stat_vote"

	for obj in sections:
		selected = 0
		if obj.has_key( instance ):
			for i in xrange(len(obj[instance][component])):
				if getVal( obj[instance][component][i][0] ) > getVal( obj[instance][notComponent][i][0] ):
					selected += 1
			values.append( str( float( selected ) / float( len( obj[instance][component] ) ) ) )
	return values


#note: sometimes results data has duplicate actual val last_states...
#to find use regex "\t\t actual val:[\V]*\n\t\t actual val:" if it exists
#remove 2nd value.
def get_precision( sections, instance="train", var="overall" ):
	values = []

	for obj in sections:
		correct = 0
		total = 0
		if obj.has_key(instance):
			for i in xrange(len(obj[instance]["graph_vote"])):
				total += 1
				val = obj[instance]["actual_val"][i]
				if var == "overall":
					if getVal( obj[instance]["graph_vote"][i][0] ) > getVal( obj[instance]["stat_vote"][i][0] ):
						if val in obj[instance]["graph_vote"][i][0]:
							correct += 1
					elif val in obj[instance]["stat_vote"][i][0]:
						correct += 1
				elif var == "optimal":
					if val in obj[instance]["graph_vote"][i][0]:
						correct += 1
					elif val in obj[instance]["stat_vote"][i][0]:
						correct += 1
				elif var == "stat_vote" or var == "graph_vote":
					if val in obj[instance][var][i][0]:
						correct += 1
				elif var == "exclusive_graph":
					if val in obj[instance]["graph_vote"][i][0] and val not in obj[instance]["stat_vote"][i][0]:
						correct += 1
				elif var == "exclusive_stat":
					if val in obj[instance]["stat_vote"][i][0] and val not in obj[instance]["graph_vote"][i][0]:
						correct += 1

			values.append( str( float( correct ) / float( total ) ))

	return values


def getVal( instanceStr ):
	dot = instanceStr.find(".")
	return float( instanceStr[dot - 1 : dot + 2] )


def getWord( instanceStr ):
	retStr = instanceStr.split(",")[0]
	return retStr


def graphify( graph ):
	output = ""

	for heading in graph[0]:
		output += ("%s & " %heading)
	output = output[0: output.rfind('&')]
	output += "\\\\ \\hline \n"

	for obj in graph[1]:
		result = ""
		for res in obj:
			if isNonFloatNum( res ):
				result += "%s & " %res
			elif isFloat( res ):
				result += "%1.2f & " %res
			else:
				result += "%s & " %res

		result = result[0: result.rfind('&')]
		result += "\\\\ \\hline \n"
		output += result
	
	return output 


def main( file_name ):
	global curr_obj

	for line in open( file_name, 'r' ):
		process_lines( line )

	####### for results values #########
	#results_graph = get_results( curr_obj )
	#output = graphify( results_graph )
	#print "results graph\n"
	####### for precision #########
	#output = get_precision( curr_obj, "train", "exclusive_graph" )
	#print "Training results (exclusive graph): \n%s" %(",".join(output))
	#output = get_precision( curr_obj, "results", "exclusive_graph" )
	#print "Test results (exclusive graph): \n%s" %(",".join(output))
	#output = get_precision( curr_obj, "train", "exclusive_stat" )
	#print "Training results (exclusive stat): \n%s" %(",".join(output))
	#output = get_precision( curr_obj, "results", "exclusive_stat" )
	#print "Test results (exclusive stat): \n%s" %(",".join(output))
	####### for biasness ##########
	#output = get_biasness( curr_obj )
	#print "biasness (training, graph): \n%s" %(",".join( output ) )
	#output = get_biasness( curr_obj, "train", "stat_vote" )
	#print "biasness (training, stats): \n%s" %(",".join( output ) )
	#output = get_biasness( curr_obj, "results" )
	#print "biasness (testing, graph): \n%s" %(",".join( output ) )
	#output = get_biasness( curr_obj, "results", "stat_vote" )
	#print "biasness (testing, graph): \n%s" %(",".join( output ) )
	####### for word checks ########
	output = get_correct_words( curr_obj )
	print "%s" %output


if __name__ == "__main__":
	parser = argparse.ArgumentParser( description='sums up the results of given output file' )
	parser.add_argument( 'file', type=str, help='location of a file that is the output of a MM-Algorithm main.py run' )
	args = parser.parse_args()

	if os.path.exists( args.file ):
		main( args.file )
	else:
		print "file not found."
