
"""
gts v0.01 

genetic trade simulator

Copyright 2011 Brian Monkaba

This file is part of ga-bitbot.

    ga-bitbot is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    ga-bitbot is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with ga-bitbot.  If not, see <http://www.gnu.org/licenses/>.
"""





# connect to the xml server
#

import xmlrpclib
import json
import gene_server_config
import time
import sys

__server__ = gene_server_config.__server__
__port__ = str(gene_server_config.__port__)

#make sure the port number matches the server.
server = xmlrpclib.Server('http://' + __server__ + ":" + __port__)  

print "Connected to",__server__,":",__port__


from bct import *
from genetic import *
from load_config import *
import pdb
import time

if __name__ == "__main__":
	__appversion__ = "0.01a"
	print "Genetic Bitcoin Trade Simulator v%s"%__appversion__

	max_length = 60 * 24 * 360
	calibrate = 1	#set to one to adjust the population size to maintain a one min test cycle

	def load():
		#open the history file
		print "loading the data set"
		f = open("./datafeed/bcfeed_mtgoxUSD_1min.csv",'r')
		#f = open("./datafeed/test_data.csv",'r')
		d = f.readlines()
		f.close()
	
		if len(d) > max_length:
			#truncate the dataset
			d [max_length * -1:]

		#load the backtest dataset
		input = []
		for row in d[1:]:
			r = row.split(',')[1] #last price
			t = row.split(',')[0] #time
			input.append([int(float(t)),float(r)])
		print "done loading:", str(len(input)),"records."
		return input
	
	#load the inital data
	input = load()
    
	#configure the gene pool
	g = genepool()
	g = load_config_into_object(load_config_from_file("gene_def.json"),g)

	#g.set_log("winners.txt")
	print "Creating the trade engine"
	te = trade_engine()
	te.score_only = True
	#preprocess input data
	te.classify_market(input)

	#process command line args
	quartile = ''
	bs = ''
	print sys.argv
	if len(sys.argv) == 3:
		# Convert the two arguments from strings into numbers
		quartile = sys.argv[1]
		bs = sys.argv[2]
	
	#which quartile group to test
	while not (quartile in ['1','2','3','4']):
		print "Which quartile group to test? (1,2,3,4):"
		quartile = raw_input()
	quartile = int(quartile)
    

	#bootstrap the population with the winners available from the gene_pool server
	while not(bs == 'y' or bs == 'n'):
		print "Bootstrap from the gene_server? (y/n)"
		bs = raw_input()
	if bs == 'y':
		bob_simulator = True
		g.local_optima_trigger = 10
		calibrate = 1
		bootstrap_bobs = json.loads(server.get_bobs(quartile))
		bootstrap_all = json.loads(server.get_all(quartile))
		print len(bootstrap_all)
		if (type(bootstrap_bobs) == type([])) and (type(bootstrap_all) == type([])):
			g.seed()
			g.pool = []		
			g.insert_genedict_list(bootstrap_bobs)
			g.insert_genedict_list(bootstrap_all)	
			g.reset_scores()
		else: #if no BOBS or high scores..seed with a new population
			print "no BOBs or high scores available...seeding new pool."
			g.seed()

		print "%s BOBs loaded"%len(bootstrap_bobs)
		print "%s high scores loaded"%len(bootstrap_all)

		print "Pool size: %s"%len(g.pool)
	
	else:
		bob_simulator = False
		g.local_optima_trigger = 5
		print "Seeding the initial population"
		g.seed()

	cycle_time = 20 * 1#time in seconds to test the entire population
	test_count = 0
	total_count = 0
	max_score = -10000
	max_score_id = -1
	start_time = time.time()
	print "Running the simulator"
	while 1:
		#print test_count #debug 
		#periodicaly reload the data set
		test_count += 1
		total_count += 1

		    
		if total_count%g.pool_size == 0:
			#benchmark the cycle speed
			current_time = time.time()
			elapsed_time = current_time - start_time
			gps = total_count / elapsed_time
			if calibrate == 1:
				print "Recalibrating pool size..."
				g.pool_size = int(gps * cycle_time)
				if g.pool_size > 10000:
					g.pool_size = 10000
			print "Genes/Sec Processed: ","%.2f"%gps,"Pool Size: ",g.pool_size,"Total Processed: ",total_count
			#load the latest trade data
			#print "Loading the lastest trade data..."
			input = load()
			#preprocess input data
			te.classify_market(input)
			#print g.local_optima_reached
		if g.local_optima_reached:
			#print '#'*10, " Local optima reached...sending bob to the gene_server ", '#'*10		
			max_score = 0
			test_count = 0
			g.max_mutate = 0.5
			g.prune_threshold = 0.2

			max_gene = g.get_by_id(max_score_id)
			if max_gene != None:
				print "--\tSubmit BOB for id:%s to server (%.2f)"%(str(max_gene['id']),max_gene['score'])
			server.put_bob(json.dumps(max_gene),quartile)
			if bob_simulator:
				#after a local optima is reached, sleep for some time to allow extra processing power to
				#the other clients so they can find potentialy better genes
				#print "going to sleep..."
				#time.sleep(60*15)
				bootstrap_bobs = json.loads(server.get_bobs(quartile))
			    	bootstrap_all = json.loads(server.get_all(quartile))
				if (type(bootstrap_bobs) == type([])) and (type(bootstrap_all) == type([])):
					g.seed()
					g.pool = []		
					g.insert_genedict_list(bootstrap_bobs)
					g.insert_genedict_list(bootstrap_all)	
					g.reset_scores()			
				else: #if no BOBS or high scores..seed with a new population
					#print "no BOBs or high scores available...seeding new pool."
					g.seed() #not sure if I need this
			else:
				#print "slicing the gene pool"
				#g.pool = g.pool[int(g.pool_size * 70):]
				g.pool = []
				g.seed()
				g.local_optima_reached = False
				#g.local_optima_buffer = []

		if test_count > (g.pool_size * 3):
			test_count = 0
			print "Reset scores to force retest of winners..."
			test_count = 0
			max_score = 0	#knock the high score down to prevent blocking
					#latest scoring data which may fall due to
					#the latest price data
			g.next_gen()
			g.reset_scores()

		#create/reset the trade engine
		te.reset()
		    
		#get the next gene
		ag = g.get_next()
		    
		#set the trade engine class vars
		#te.buy_delay = len(input) - (60 * 12)
		te.shares = ag['shares']
		te.wll = ag['wll'] + ag['wls'] + 2 #add the two together to make sure
					    #the macd moving windows dont get inverted
		te.wls = ag['wls'] + 1
		te.buy_wait = ag['buy_wait']
		te.markup = ag['markup'] + (te.commision * 3.0) #+ 0.025
		te.stop_loss = ag['stop_loss']
		te.stop_age = ag['stop_age']
		te.macd_buy_trip = ag['macd_buy_trip'] * -1.0
		#te.min_i_neg = ag['min_i_neg']
		#te.min_i_pos = ag['min_i_pos']
		te.buy_wait_after_stop_loss = ag['buy_wait_after_stop_loss']
		#feed the input through the trade engine

		te.test_quartile(quartile)

		try:
			for i in input:
				te.input(i[0],i[1])
		except:
			#kill off any genes that crash the trade engine (div by 0 errors for instance)
			g.set_score(ag['id'],g.kill_score)
		else:
			#return the score to the gene pool
			score = te.score()
			print score
			g.set_score(ag['id'],score)
			g.set_message(ag['id'],"Balance: " + str(te.balance) +"; Wins: " + str(te.wins)+ "; Loss:" + str(te.loss) +  "; Positions: " + str(len(te.positions)))

			#if a new high score is found (or revisited) submitt the gene to
			#the server
			if score > max_score:
				print "--\tSubmit high score for id:%s to server (%.2f)"%(str(ag['id']),score)
				max_score = score
				max_score_id = ag['id']
				max_gene = g.get_by_id(max_score_id)
				if max_gene != None:
					server.put(json.dumps(max_gene),quartile)
				else:
					print "MAX_GENE is None!!"


