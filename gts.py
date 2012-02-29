
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
import random
import __main__
random.seed(time.time())

__server__ = gene_server_config.__server__
__port__ = str(gene_server_config.__port__)

#make sure the port number matches the server.
server = xmlrpclib.Server('http://' + __server__ + ":" + __port__)  

print "Connected to",__server__,":",__port__


from bct import *
#from trade_engine import *
from genetic import *
from load_config import *
import pdb


if __name__ == "__main__":
	__appversion__ = "0.01a"
	print "Genetic Bitcoin Trade Simulator v%s"%__appversion__
	

	#the variable values below are superceded by the configuration loaded from the 
	#configuration file global_config.json
	#!!!!!!!! to change the values edit the json configuration file NOT the variables below !!!!!!!!
	max_length = 60 * 24 * 60
	load_throttle = 1 #go easy on cpu usage
	load_throttle_sleep_interval = 0.10#seconds
	calibrate = 1	#set to one to adjust the population size to maintain a one min test cycle
	cycle_time = 60 * 1#time in seconds to test the entire population
	min_cycle_time = 30
	cycle_time_step = 2
	pid_update_rate = 20 #reset watchdog after every n genes tested
	enable_flash_crash_protection = False
	flash_crash_protection_delay = 60 * 3 #three hours
	config_loaded = 0

	#load config
	try:
		__main__ = load_config_file_into_object('global_config.json',__main__)
	except:
		print "Error detected while loading the configuration. The application will now exit."
		import sys
		sys.exit()
	else:
		if config_loaded == False:
			print "Configuration failed to load. The application will now exit."
			import sys
			sys.exit()
		else:
			print "Configuration loaded."


	quartile_cycle = False

	def load():
		#open the history file
		#print "loading the data set"
		f = open("./datafeed/bcfeed_mtgoxUSD_1min.csv",'r')
		#f = open("./datafeed/test_data.csv",'r')
		d = f.readlines()
		f.close()
	
		if len(d) > max_length:
			#truncate the dataset
			d = d[max_length * -1:]

		#load the backtest dataset
		input = []
		for row in d[1:]:
			r = row.split(',')[1] #last price
			t = row.split(',')[0] #time
			input.append([int(float(t)),float(r)])
		#print "done loading:", str(len(input)),"records."
		return input

	#process command line args
	quartile = ''
	bs = ''
	verbose = False
	run_once = False
	get_config = False

	print sys.argv
	if len(sys.argv) >= 3:
		# Convert the two arguments from strings into numbers
		quartile = sys.argv[1]
		bs = sys.argv[2]
		if len(sys.argv) > 3:
			for i in range(3,len(sys.argv)):
				if sys.argv[i] == 'v':
					verbose = True
				if sys.argv[i] == 'run_once':
					#use with gal.py to auto reset (to address pypy memory leaks)
					#exit after first local optima found
					#or in the case of 'all' quartiles being tested, reset after once cycle through the quartiles
					run_once = True
				if sys.argv[i] == 'get_config':
					#if set the gene_def config will be randomly loaded from the server
					get_config = True
	
	#which quartile group to test
	while not (quartile in ['1','2','3','4','all']):
		print "Which quartile group to test? (1,2,3,4):"
		quartile = raw_input()
	if quartile != 'all':	
		quartile = int(quartile)
	else:
		quartile = 1
		quartile_cycle = True
    		update_all_scores = True

	#configure the gene pool
	g = genepool()
	if get_config == True:
		print "Loading random gene_def from the server."
		gd = "UNDEFINED"
		while gd == "UNDEFINED" and get_config == True:
			#get the gene def config from the server
			gdhl = json.loads(server.get_gene_def_hash_list())
			if len(gdhl) < 2:
				#the default config isn't defined
				#if there are less then two genes registered then switch to the local config.
				get_config = False
				break
			#pick one at random
			gdh = random.choice(gdhl)
			#get the gene_def
			gd = server.get_gene_def(gdh)
			#print gd
			if gd != "UNDEFINED":
				try:
					gd = json.loads(gd)
					#load the remote config
					g = load_config_into_object(gd,g)
					#only need to register the client with the existing gene_def hash
					server.pid_register_client(g.id,gdh)
					print "gene_def_hash:",gdh
					print "name",gd['name']
	 				print "description",gd['description']
					print "gene_def load complete."
				except:
					print "gene_def load error:",gd
					gd = "UNDEFINED"
					get_config = False #force load local gen_def.json config

	#ad = json.loads(json.loads(server.get_gene_def(random.choice(json.loads(server.get_gene_def_hash_list())))))

	if get_config == False:	
		g = load_config_into_object(load_config_from_file("gene_def.json"),g)

		#register the gene_def file and link to this client using the gene pool id as the PID (GUID)
		f = open('./config/gene_def.json','r')
		gdc = f.read()
		f.close()
		server.pid_register_gene_def(g.id,gdc)

	#reset the process watchdog
	server.pid_alive(g.id)

	#load the inital data
	input = load()

	#g.set_log("winners.txt")
	print "Creating the trade engine"
	te = trade_engine()
	te.score_only = True
	te.enable_flash_crash_protection = enable_flash_crash_protection 
	te.flash_crash_protection_delay = flash_crash_protection_delay
	#preprocess input data
	te.classify_market(input)

	#bootstrap the population with the winners available from the gene_pool server
	while not(bs == 'y' or bs == 'n'):
		print "Bootstrap from the gene_server? (y/n)"
		bs = raw_input()
	if bs == 'y':
		bob_simulator = True
		if quartile_cycle == False:
			update_all_scores = False
		g.local_optima_trigger = 10
		bootstrap_bobs = json.loads(server.get_bobs(quartile))
		bootstrap_all = json.loads(server.get_all(quartile))
		print len(bootstrap_all)
		if (type(bootstrap_bobs) == type([])) and (type(bootstrap_all) == type([])):
			g.seed()
			if len(bootstrap_all) > 100:
				g.pool = []		
			g.insert_genedict_list(bootstrap_bobs)
			g.insert_genedict_list(bootstrap_all)
			g.pool_size = len(g.pool)
			if quartile_cycle == True:
				#reset the scores for retesting
				g.reset_scores()
			else:
				#mate the genes before testing
				g.next_gen() 
		else: #if no BOBS or high scores..seed with a new population
			print "no BOBs or high scores available...seeding new pool."
			g.seed()

		print "Update all scores:",update_all_scores
		print "%s BOBs loaded"%len(bootstrap_bobs)
		print "%s high scores loaded"%len(bootstrap_all)

		print "Pool size: %s"%len(g.pool)
	
	else:
		bob_simulator = False
		update_all_scores = False
		g.local_optima_trigger = 5
		print "Seeding the initial population"
		g.seed()

	#the counters are all incremented at the same time but are reset by different events:
	test_count = 0  #used to reset the pool after so many loop cycles
	total_count = 0 #used to calculate overall performance
	loop_count = 0  # used to trigger pool size calibration and data reload

	max_score = -10000
	max_score_id = -1
	start_time = time.time()
	print "Running the simulator"
	while 1:
		#print test_count #debug 
		#periodicaly reload the data set
		test_count += 1
		total_count += 1
		loop_count += 1
		if load_throttle == 1:
			time.sleep(load_throttle_sleep_interval)

		if loop_count%pid_update_rate == 0:
			#periodicaly reset the watchdog monitor
			#print "resetting watchdog timer"
			server.pid_alive(g.id)

		if loop_count > g.pool_size:
			if quartile_cycle == True and bob_simulator == True:
				#force a state jump to load the next quartile to retest the genes
				#in this mode the only function of the client is to cycle through the quartiles to retest existing genes
				g.local_optima_reached = True 

			update_all_scores = False	#on the first pass only, bob clients need to resubmit updated scores for every gene 
			loop_count = 0
			#reset the watchdog monitor
			server.pid_alive(g.id)
			#benchmark the cycle speed
			current_time = time.time()
			elapsed_time = current_time - start_time
			gps = total_count / elapsed_time
			pid_update_rate = int(gps * 40)
			if calibrate == 1:
				#print "Recalibrating pool size..."
				g.pool_size = int(gps * cycle_time)
				cycle_time -= cycle_time_step
				if cycle_time < min_cycle_time:
					cycle_time = min_cycle_time
				if g.pool_size > 10000:
					g.pool_size = 10000
			performance_metrics = "%.2f"%gps,"G/S; ","%.2f"%((gps*len(input))/1000.0),"KS/S;","  Pool Size: ",g.pool_size,"  Total Processed: ",total_count
			performance_metrics = " ".join(map(str,performance_metrics))
			print performance_metrics
			server.pid_msg(g.id,performance_metrics)
			
		if g.local_optima_reached:	
			test_count = 0

			#load the latest trade data
			#print "Loading the lastest trade data..."
			input = load()
			#preprocess input data
			te.classify_market(input)

			if quartile_cycle == True and bob_simulator == True:
				#jump to the next quartile and skip the bob submission
				update_all_scores = True
				quartile += 1
				if quartile > 4:
					quartile = 1
					if run_once:
						print "Run Once Done."
						server.pid_exit(g.id)
						sys.exit()
			

			elif max_gene != None:
				#debug
				print max_gene
				#end debug
				print "--\tSubmit BOB for id:%s to server (%.2f)"%(str(max_gene['id']),max_gene['score'])
				server.put_bob(json.dumps(max_gene),quartile)
				if quartile_cycle == True:
					#if not in bob simulator mode but cycling is enabled then 
					#the client will cycle through the quartiles as local optimas are found
					#jump to the next quartile
					quartile += 1
					if quartile > 4:
						quartile = 1
						if run_once:
							print "Run Once Done."
							server.pid_exit(g.id)
							sys.exit()
			else:
				if max_score > -10000:
					print "**WARNING** MAX_GENE is gone.: ID",max_score_id
					print "*"*80
					print "GENE DUMP:"
					for ag in g.pool:
						print ag['id'],ag['score']
					print "*"*80
					print "HALTED."
					sys.exit()

			max_gene = None #clear the max gene
			max_score = -10000 #reset the high score

			if quartile_cycle == False and run_once:
				print "Run Once Done."
				server.pid_exit(g.id)
				sys.exit()

			if bob_simulator:
				#update_all_scores = True	#on the first pass only, bob clients need to resubmit updated scores for every gene 
				bootstrap_bobs = json.loads(server.get_bobs(quartile))
			    	bootstrap_all = json.loads(server.get_all(quartile))
				g.pool_size = len(g.pool)
				if (type(bootstrap_bobs) == type([])) and (type(bootstrap_all) == type([])):
					g.seed()
					g.pool = []		
					g.insert_genedict_list(bootstrap_bobs)
					g.insert_genedict_list(bootstrap_all)
					if quartile_cycle == True:
						#reset the scores for retesting
						g.reset_scores()
					else:
						#mate the genes before testing
						g.next_gen() 
					
				else: #if no BOBS or high scores..seed with a new population
					#print "no BOBs or high scores available...seeding new pool."
					g.seed()
			else:
				g.seed()

		if test_count > (g.pool_size * 10):
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
		
		#configure the trade engine
		te = load_config_into_object({'set':ag},te)

		#set the quartile to test
		te.test_quartile(quartile)

		#feed the input through the trade engine
		try:
			for i in input:
				te.input(i[0],i[1])
		except:
			#kill off any genes that crash the trade engine (div by 0 errors for instance)
			g.set_score(ag['id'],g.kill_score)
		else:
			#return the score to the gene pool
			score = te.score()
			if verbose:
				print ag['gene'],"\t".join(["%.5f"%max_score,"%.5f"%score,"%.3f"%g.prune_threshold])
			g.set_score(ag['id'],score)
			g.set_message(ag['id'],"Balance: " + str(te.balance) +"; Wins: " + str(te.wins)+ "; Loss:" + str(te.loss) +  "; Positions: " + str(len(te.positions)))

			#if a new high score is found submit the gene to the server
			if score > max_score:
				print "--\tSubmit high score for quartile:%s id:%s to server (%.5f)"%(str(quartile),str(ag['id']),score)
				max_score = score
				max_score_id = ag['id']
				max_gene = ag.copy() #g.get_by_id(max_score_id)
				if max_gene != None:
					server.put(json.dumps(max_gene),quartile)
				else:
					print "MAX_GENE is None!!"
			elif update_all_scores == True:
				print "--\tUpdating score for quartile:%s id:%s to server (%.5f)"%(str(quartile),str(ag['id']),score)
				agene = g.get_by_id(ag['id'])
				if agene != None:
					server.put(json.dumps(agene),quartile)
				else:
					print "Updating Gene Error: Gene is missing!!"



