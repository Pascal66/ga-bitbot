#!/usr/bin/python

"""
gene_server v0.01 

- a xmlrpc server providing a storage/query service for the GA trade system

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
#   gene server
#	- a xmlrpc server providing a storage/query service for the GA trade system
#

import gene_server_config
__server__ = gene_server_config.__server__
__port__ = gene_server_config.__port__
__path__ = "/gene"


import sys
import time
import json
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
from operator import itemgetter, attrgetter

max_len = 600
max_bobs = 1000
g_d = [[],[],[],[]]
g_trgt = []

g_bobs = [[],[],[],[]]

def echo(msg):
	return msg

def put_target(target):
	global g_trgt
	g_trgt = target
	return "OK"

def get_target():
	global g_trgt
	return g_trgt

def get_gene(n_sec,quartile):
	global g_d
	
	t = time.time() - n_sec
	#get the highest score calculated within the last n seconds
	#or return the latest if none are found.
	r = []
	#collect the records (presorted))
	for a_d in g_d[quartile - 1]:
		if a_d['time'] > t:
			r.append(a_d)
		else:
			break
	#print "searching for greater than",t 
	#print "found",len(r),"records"
	#if no record found, grab the most recent
	if len(r) == 0:
		r = g_d[quartile - 1][0]
	
	if len(r) > 1:
		#if more than one record found find the highest scoring one
		r = sorted(r, key=itemgetter('score'),reverse = True)[0]

	print "get",r['time'],r['score']
		
	return json.dumps(r)

def get_all_genes(quartile):
	global g_d
	return json.dumps(g_d[quartile - 1])

def get_bobs(quartile):
	global g_bobs
	return json.dumps(g_bobs[quartile - 1])

def put_gene(d,quartile):
	global g_d
	#dictionary must have two key values, time & score
	#add the record and sort the dictionary list
	d = json.loads(d)
	g_d[quartile - 1].append(d)
	d = sorted(g_d[quartile - 1], key=itemgetter('time'),reverse = True)
	g_d[quartile - 1] = d
	
	print "put",g_d[quartile - 1][0]['time'],g_d[quartile - 1][0]['score']
	#prune the dictionary list
	if len(g_d[quartile - 1]) > max_len:
		g_d[quartile - 1] = g_d[quartile - 1][:max_len]
	return "OK"

def put_bob(d,quartile):
	global g_bobs
	#dictionary must have two key values, time & score
	#add the record and sort the dictionary list
	d = json.loads(d)

	if any(adict['gene'] == d['gene'] for adict in g_bobs[quartile - 1]):
		print "put_bob: duplicate gene rejected"
		return "OK"

	g_bobs[quartile - 1].append(d)
	s_bobs = sorted(g_bobs[quartile - 1], key=itemgetter('score'),reverse = True)
	g_bobs[quartile - 1] = s_bobs
	
	print "put bob",d['time'],d['score']
	#prune the dictionary list
	if len(g_bobs[quartile - 1]) > max_bobs:
		g_bobs[quartile - 1] = g_bobs[quartile - 1][:max_bobs]
	return "OK"


#set the service url
class RequestHandler(SimpleXMLRPCRequestHandler):
	rpc_paths = ('/gene','/RPC2')

#create the server
server = SimpleXMLRPCServer((__server__, __port__),requestHandler = RequestHandler,logRequests = True, allow_none = True)

#register the functions
server.register_function(get_target,'get_target')
server.register_function(put_target,'put_target')
server.register_function(get_gene,'get')
server.register_function(get_all_genes,'get_all')
server.register_function(put_gene,'put')
server.register_function(put_bob,'put_bob')
server.register_function(get_bobs,'get_bobs')
server.register_function(echo,'echo')
server.register_introspection_functions()

if __name__ == "__main__":
	print "gene_server: running on port %s"%__port__
	while 1:
		server.handle_request()

