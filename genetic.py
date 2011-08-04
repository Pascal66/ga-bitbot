
"""
genetic v0.01 

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

import random
import time
from operator import itemgetter
import pdb

#seed the random number generator
random.seed(time.time())

def zero(a):
	return 0

#create a gene pool
class genepool:
    def __init__(self):
	self.prune_threshold = 0.70	#score threshold - percentile (top n%)
	self.max_prune_threshold = 0.70	#score threshold - percentile (top n%)
	self.min_prune_threshold = 0.10	#score threshold - percentile (top n%)
	self.step_prune_threshold_rate = 0.01#score threshold - step down increment

	self.mutate = 0.20		#mutation rate
	self.max_mutate = 0.50		#max/min mutation rates
	self.min_mutate = 0.00		#adds support for adaptive mutation rates
	self.step_mutate_rate = 0.0001		#step down increment

	self.multiple_parent = 0.05	#multiple parent rate
	self.max_multiple_parents = 7	#maximum number of multi parent merge (per parent)
	self.niche_trigger = 3		#trigger niche filter when n bits or less don't match
	self.niche_threshold = 0.95	#(calculated!) niche filter threshold for fitering similar genes
	self.pool_size = 1000		#min pool size (working size may be larger)
	self.pool_family_ratio = 0.9	#pct of the pool to be filled w/ offspring
	self.pool_max_survivor_ratio = 0.3	#max survivor pool ratio
	self.kill_score = -100000
	self.pool= []			#gene pool
	self.contains = []		#gene data config
	self.genelen = 0 		#calculated gene length	
	self.iteration = 0		#current iteration
	self.max_iteration = 100000000	#max iteration before kill off
	self.log_enable = False
	self.log_filename = ""
	self.local_optima_reached = False	#flag to indicate when a local optima has been reached
	self.local_optima_trigger = 20		#number of iterations with no increase in score required to trigger
	self.local_optima_buffer = [] 		#the local optima flag. The buffer maintains the last high scores

    def step_prune(self):
	if self.prune_threshold > self.min_prune_threshold:
		self.prune_threshold -= self.step_prune_threshold_rate
	else:
		self.prune_threshold = self.max_prune_threshold

    def step_mutate(self):
	if self.mutate > self.min_mutate:
		self.mutate -= self.step_mutate_rate
	else:
		self.mutate = self.max_mutate


    def set_log(self,filename):
	self.log_enable = True
	self.log_filename = filename

    def log_dict(self,msg):
	try:
	    msg.keys()
	except:
	    #empty dict - nothing to log
	    return
	if self.log_enable == True:
	    f = open(self.log_filename,'a')
	    f.write(str(msg) + '\n')
	    f.close()
	
	#print "-"*40
	#print "Winning Gene:"
	#for key in msg.keys():
	#    print key," : ",msg[key]

    def reset_scores(self):
	#Reset the scores in the gene pool
	for g in self.pool:
	    g['score'] = None
	    g['time'] = None
		
    def mutate_gene(self,c):
	self.step_mutate()
	
	m = ""
	for bit in c:
	    if random.random() > (1 - self.mutate):
		bit = str(int(bool(bit) ^ bool(1))) #xor
	    m += bit
		
	return m
    
    def niche_filter(self,pool):
	#filter out similar genes to the winner
	#to maintain population diversity
	if len(pool) < 2:	#only run the filter if there are genes available
		return pool
	#calculate the niche_threshold
	self.niche_threshold = (self.genelen - self.niche_trigger) / float(self.genelen)

	winner = pool[0]['gene']
	ret_pool = [pool[0]]
	for i in range(1,len(pool)):
		match = 0
		for j in range(self.genelen):
			if pool[i]['gene'][j] == winner[j]:
				match += 1
		if match / float(self.genelen) >= self.niche_threshold:
			#gene is similar - filter it out
			#print "filtered similar gene",pool[i]['gene']
			pass
		else:
			ret_pool.append(pool[i])
	return ret_pool


    def merge_multi(self,alist):
	#adds support for arb number of multiple parents
	#merge by majority vote 
	# - need at least three to merge (duh!)
	# - and should be an odd number (no tied votes)
	if len(alist) < 3:
		print "need at least three genes to merge"
	n = len(alist[0])
	half_n = n/2.0
	sums = map(zero,range(n))
	for item in alist:
		for i in range(len(item)):
			if item[i] == '1':
				sums[i] += 1
	#build the merged gene
	g = ""
	for asum in sums:
		if asum >= half_n:
			g += "1"
		else:
			g += "0" 	
	return g

    def mate(self,a,b):
	# To create diveristy in the population..
	# Some will be mated, some will be mated and mutated and some will be
	# mutated but not mated. @ 33%/33%/33%
	
	#splice two genes (66% probablility)
	if random.random() >= 0.33:	    
	    l = len(a)
	    splice = int(random.random() * l)
	    c = a[:splice] + b[splice:]
	    #mutate the children (50% probability)
	    if random.random() > 0.5:
		c = self.mutate_gene(c)
	else:
	    #select one of the parents (50% probability)
	    #and mutate it (33% probability)
	    if random.random() > 0.5:
		c = a
	    else:
		c = b
	    c = self.mutate_gene(c)
		
	return c
    
    def next_gen(self):
	#populate the pool with the next generation
	self.iteration += 1
	scores = []
	max_score = -99999
	winning_gene = ""
    
	#sort the genes by score
	self.pool = sorted(self.pool, key=itemgetter('score'),reverse=True)
	if len(self.pool) < 2:
		self.seed()


	winning_gene = self.pool[0]
	max_score = winning_gene['score']
	self.log_dict(winning_gene)

	#test for local optima
	if max_score != None:
		self.local_optima_buffer.append(max_score)
	if len(self.local_optima_buffer) > self.local_optima_trigger:
		self.local_optima_buffer = self.local_optima_buffer[1:]

	if len(self.local_optima_buffer) == self.local_optima_trigger:
		#print sum(self.local_optima_buffer),self.local_optima_trigger,max_score
		#print (sum(self.local_optima_buffer) / self.local_optima_trigger) - max_score
		if abs((sum(self.local_optima_buffer) / self.local_optima_trigger) - max_score) < 0.000001:
			#local optima reached
			print "#"*25,"local optima reached","#"*25
			self.local_optima_reached = True

	#remove survivor twins
	gen = self.pool
	filtered_gen = []
	tlist = []
	for i in range(len(gen)):
	    if gen[i]['gene'] in tlist:
		#twin found ignore
		pass
	    else:
		tlist.append(gen[i]['gene'])
		filtered_gen.append(gen[i])
	gen = filtered_gen

	#apply the threshold
	self.step_prune()	#variable pruning threshold
	threshold = int(len(gen) * self.prune_threshold)
	gen = gen[:threshold]

	#apply the niche filter
	#gen = self.niche_filter(gen)

	#make sure there are at least three genes available (even if they're twins)
	if len(gen) < 3:
		gen = self.pool[0:3]


	#generate offspring
	os = []
	if len(gen) > 1:
	    for i in range(int(self.pool_size * self.pool_family_ratio)  - len(gen)):
		if random.random() < self.multiple_parent:
			n_merge = int(random.random() * self.max_multiple_parents)
			if n_merge < 3:	#make sure the min number of samples are taken
				n_merge = 3
			if n_merge%2 == 0: #make sure there are an odd number of samples
				n_merge += 1 
			#collect the samples
			m_l = []
			f_l = []
			max_m = 0
			for j in range(n_merge):
				m = int(random.random() * len(gen))
				f = int(random.random() * len(gen))
				m_l.append(gen[m]['gene'])
				f_l.append(gen[f]['gene'])
				if m > max_m:		
					max_m = m
			m = max_m #transfer the oldest generation id from the sample to the offspring
			mm = self.merge_multi(m_l)	#multi parent merge - male
			mf = self.merge_multi(f_l)	#multi parent merge - female
			new_g = self.mate(mm,mf)
		else:
			m = int(random.random() * len(gen))
			f = int(random.random() * len(gen))
			new_g = self.mate(gen[m]['gene'],gen[f]['gene'])
		gdict = {"gene":new_g,"score":None,"time":None,"generation":gen[m]["generation"] + 1,"id":int(random.random()*999999999),"msg":""}
		os.append(gdict)

	#if max iterations have been reached repopulate
	#the gene pool
	if self.iteration >= self.max_iteration:
	    self.iteration = 0
	    winning_gene['score'] = 0 #reset the score
	    gen = [winning_gene]
	    os = []
	    print "*"*10,"NEW POPULATION","*"*10		
	
	
	self.pool = gen + os
	
	#create some fresh genes if pool space is available
	new_gene_count = 0
	while len(self.pool) < self.pool_size:
	    new_gene_count += 1
	    self.pool.append(self.create_gene())
	
	#decode the genes 
	self.decode()	 

	print "Survivors",len(gen)	
	print "Offspring",len(os)
	print "New",new_gene_count  
	print "Pool Size:",len(self.pool)
	print "Threshold:",self.prune_threshold
	print "Mutate:",self.mutate
	print "-" * 80
	
    def get_next(self):
	#get the next available unscored gene
	#if none are available the create the
	#next generation
	for g in self.pool:
	    if g['score'] == None:
		return g
	#out of unscored genes
	self.next_gen()
	return self.get_next()
    
    def get_by_id(self,id):
	for g in self.pool:
	    if g['id'] == id:
		return g
	return None
	
    def set_score(self,id,score):
	#set the score for a gene
	for g in self.pool:
	    if g['id'] == id:
		g['score'] = score
		g['time'] = time.time()
	return
    
    def set_message(self,id,msg):
	#set the message for a gene (basicaly tag a note on the gene)
	for g in self.pool:
	    if g['id'] == id:
		g['msg'] = msg
	return
    
    def add_numvar(self,name,bits,decimal_places):
	#add a variable to the gene
	self.contains.append([name,bits,decimal_places])
    
    def rbit(self):
	#generate a random bit
	if random.random() > 0.5:
	    return "1"
	else:
	    return "0"
	
    def calc_genelen(self):
	#calculate the gene length (bits)
	self.genelen = 0
	for item in self.contains:
	    self.genelen += item[1]
	
    def decode(self):
	#decode the gene pool into key:value dictionarys
	for g in self.pool:
	    offset = 0
	    for v in self.contains:
		name = v[0]
		glen = v[1]
		subg = g['gene'][offset:offset+glen]
		offset += glen
		n = int(subg,2)
		if v[2] > 0:
		    n = (n * 1.0) / pow(10,v[2])
		g[name] = n
		
    def decode_gene_dict(self,g_d):
	offset = 0
	for v in self.contains:
		name = v[0]
		glen = v[1]
		subg = g_d['gene'][offset:offset+glen]
		offset += glen
		n = int(subg,2)
		if v[2] > 0:
		    n = (n * 1.0) / pow(10,v[2])
		g_d[name] = n
	return g_d


    
    def create_gene(self):
	gene = ""
	for j in range(self.genelen):
	    gene += self.rbit()
	gdict = {"gene":gene,"score":None,"time":None,"generation":1,"id":int(random.random()*999999999),"msg":""}
	for v in self.contains:
	    gdict.update({v[0]:0})
	return gdict

    def insert_genedict(self,g_d):
	self.pool.append(g_d)
	return

    def insert_genedict_list(self,g_dl):
	for g_d in g_dl:
		self.pool.append(g_d)
	return


    def insert_genestr(self,gene):
	g_d = self.create_gene()
	g_d['gene'] = gene
	g_d = self.decode_gene_dict(g_d)
	self.pool.append(g_d)
	return g_d

    def insert_genestr_list(self,gene_list):
	for gene in gene_list:
		self.insert_gene(gene)
	return

    def seed(self):
	self.pool = []
	self.local_optima_reached = False
	self.local_optima_buffer = []
	self.calc_genelen()
	for i in range(self.pool_size):
	    gdict = self.create_gene()
	    self.pool.append(gdict)
	self.decode()
    

if __name__ == "__main__":
    #test the genetic class    
    g = genepool()
   
    #16 bit number (65535) with the decimal three places to the left (10^3 = 1000)
    #max value should be 65.535
    g.add_numvar("afloat",16,3)
    
    g.add_numvar("aint",6,0)
	
    g.seed()
    
    print g.contains
    
    max_score = 0
    max_gene = ""

    while g.local_optima_reached == False:
	ag = g.get_next()
	score = ag['afloat'] * ag['aint']
	if score > max_score:
		max_score = score
		max_gene = ag['gene']
	g.set_score(ag['id'],ag['afloat'] * ag['aint'])
    print max_score
    print max_gene

    #test merge_multi
    l = ["101","010","110"]
    if g.merge_multi(l) != "110":
	print "merge_multi error"
    else:
	print "merge_multi pass"

	
	
