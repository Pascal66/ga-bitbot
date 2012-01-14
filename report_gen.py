
"""
report_gen v0.01 

report generator

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
 
#
#	Generates GA trade simulation reports using the gene server
#	Also calculates & submits the next buy trigger
#

__appversion__ = "0.01a"
print "Genetic Bitcoin Report Generator v%s"%__appversion__
# connect to the xml server
#

import xmlrpclib
import json
import gene_server_config
import time


__server__ = gene_server_config.__server__
__port__ = str(gene_server_config.__port__)

#make sure the port number matches the server.
server = xmlrpclib.Server('http://' + __server__ + ":" + __port__)  

print "Connected to",__server__,":",__port__


from bct import *


max_length = 60 * 24 * 60

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


while 1:
	skip_sleep_delay = False #default to sleep delay mode between cycles
				#will be set to true (and skip the sleep delay) if target prices are found.
	print "_" * 80
	print time.ctime()  
	#load the data set
	input = load()
	
	buys = []
	targets = []
	for quartile in [4,3,2,1]:
		#create the trade engine	
		te = trade_engine()
		#get the high score gene from the gene server
		while 1:
			try:
				ag = json.loads(server.get(60*60*24,quartile))
				break
			except:
				print "Gene Server Error"
				time.sleep(10)
		
		if type(ag) == type([]):
			ag = ag[0]
		
		#THE FOLLOWING SECTION MUST MATCH THE GTS Tool!!!
		#set the trade engine class vars
		#te.buy_delay =  len(input) - (60 * 12)
		te.shares = ag['shares']
		te.wll = ag['wll'] + ag['wls'] + 2 #add the two together to make sure
					#the macd moving windows dont get inverted
		te.wls = ag['wls'] + 1
		te.buy_wait = ag['buy_wait']
		te.markup = ag['markup'] + (te.commision * 3.0) #+ 0.025
		te.stop_loss = ag['stop_loss']
		te.stop_age = ag['stop_age']
		te.macd_buy_trip = ag['macd_buy_trip'] * -1.0
		te.buy_wait_after_stop_loss = ag['buy_wait_after_stop_loss']
		#feed the input through the trade engine
		
		#preprocess the data
		current_quartile = te.classify_market(input)
		#select the quartile to test
		te.test_quartile(quartile)
		te.net_worth_log = []

		print "_" * 40
		if current_quartile == quartile:
			print "Quartile:",quartile, "(%.4f)"%ag['score'],"+active"
		else:
			print "Quartile:",quartile, "(%.4f)"%ag['score']

		#feed the data
		try:
			for i in input:
				te.input(i[0],i[1])
		except:
			print "Gene Fault"
		else:

			# Calc the next buy trigger point
			if len(te.positions) > 0:
				#testing
				print "Inverse MACD Result: ",te.inverse_macd()

				#target = te.input_log[-1][1] - (abs(((te.macd_buy_trip - te.macd_pct_log[-1][1]) / 100.0) * te.input_log[-1][1]) * 2.0)
				#print "Simple Calculation Result: ",target
				
				#DEBUG : use the inverse MACD
				target = te.inverse_macd()

				if target > te.input_log[-1][1]:
					target = te.input_log[-1][1]

				#first check to see if the tested input triggered a buy:
				if te.positions[-1]['buy_period'] == len(te.input_log) - 1:
					p = te.positions[-1]
					target = p['buy']
				else:
					print "Last buy order was", len(te.input_log) - te.positions[-1]['buy_period'],"periods ago."
					#if not try to calculate the trigger point to get the buy orders in early...
					#print "Trying to trigger with: ",target
					print "Score: ",te.score()
					st = input[-1][0] + 2000
					te.input(st,target)
					p = te.positions[-1].copy()
					if p['buy'] != target:
						#print "Order not triggered @",target
						p['buy'] = 0.00
						p['target'] = 0.00

				#te.classify_market(input)
				print "creating charts..."
				te.chart("./report/chart.templ","./report/chart_test_%s.html"%str(quartile))
				te.chart("./report/chart.templ","./report/chart_test_zoom_%s.html"%str(quartile),60*48)
				te.chart("./report/chart.templ","./report/chart_test_now_%s.html"%str(quartile),60* 4)
				#print "Evaluating target price"
				if current_quartile == quartile:
					if ((target >= p['buy']) or (abs(target - p['buy']) < 0.01)) and p['buy'] != 0: #submit the order at or below target
						#format the orders
						p['buy'] = float("%.3f"%(p['buy'] - 0.01))
						p['target'] = float("%.3f"%p['target'])
						p.update({'stop_age':(60 * te.stop_age)})
						if float("%.3f"%((te.wins / float(te.wins + te.loss)) * 100)) > 90.0:
							#only submit an order if the win/loss ratio is greater than x%
							print "sending target buy order to server @ $" + str(p['buy'])
							server.put_target(json.dumps(p))
							skip_sleep_delay = True #if target buy orders are active skip the sleep delay
						else:
							print "underperforming trade strategy, order not submitted"
							p['buy'] = 0.00
							p['target'] = 0.00
							server.put_target(json.dumps(p))
						print "-" * 40
						print "Quartile  :",quartile
						print "Buy	   :$", p['buy']
						print "Target	:$",p['target']
						print "Win Ratio :","%.3f"%((te.wins / float(te.wins + te.loss)) * 100),"%"
						print "-" * 40
					else:
						print "Trigger criteria not met, no order set."
						print "Buy	   :$", p['buy']
						print "Target	:$",p['target']
						print "Input Target :$",target
						print "Last Price:$",input[-1][1]
						print "MACD Log: ",te.macd_pct_log[-1][1]
						print "MACD Trip: ",te.macd_buy_trip
						p.update({'stop_age':(60 * te.stop_age)}) #DEBUG ONLY!! - delete when done.
						p['buy'] = 0.00
						p['target'] = 0.00
						server.put_target(json.dumps(p))

					buys.append(p['buy'])
					targets.append(p['target'])
	#log the orders
	#f = open("./report/rg_buys.csv",'a')
	#f.write(",".join(map(str,buys)) + ",")
	#f.write(",".join(map(str,targets)) + "\n")
	#f.close()

	#create the gene visualizer report
	print "creating the gene visualizer report..."
	f = open('./report/gene.templ','r')
	template = f.read()
	f.close()

	for quartile in [1,2,3,4]:
		band_l = []
		gl = json.loads(server.get_bobs(quartile))
		if len(gl) > 0:
			#place a band (a small list of gene set to all 1's) in the data to highlight the break between the bobs and high scores
			band = "1" * len(gl[0]['gene'])
			for i in xrange(3):
				band_l.append({'gene':band})
		gl += band_l
		gl += json.loads(server.get_all(quartile))
		l = []
		for ag in gl:
			l.append(ag['gene'])
		qs = '{Q%s}'%str(quartile)
		template = template.replace(qs,str(l).replace('u',''))

	template = template.replace('{LAST_UPDATE}',time.ctime())
	f = open('./report/gene_visualizer.html','w')
	f.write(template)
	f.close()


	if skip_sleep_delay == False:
		print "sleeping..."
		print "_" * 80
		print "\n"
		time.sleep(90) #generate a report every n seconds
	else:
		print "skipping sleep state due to active trigger prices..."
		print "_" * 80
		print "\n"
