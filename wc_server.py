
"""
wc_server v0.01 

web client server

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
#	server provides a web based client interface
#

__appversion__ = "0.01a"
print "Genetic Bitcoin Web Client Server v%s"%__appversion__

# connect to the xml server
#
import gene_server_config
import xmlrpclib
import json
import time
import socket

#define the server port
PORT = 8080

#cross-platform hack to get the local ip address
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("www.google.com",80))
ip_address = s.getsockname()[0]
s.close()

__server__ = gene_server_config.__server__
__port__ = str(gene_server_config.__port__)

#make sure the port number matches the server.
server = xmlrpclib.Server('http://' + __server__ + ":" + __port__)  

print "Connected to",__server__,":",__port__


#utility functions
def ppdict(d,nest=0):
	#pretty print a dict
	if nest > 0:
		output = '<br>'
	else:
		output = ''
	try:
		for key in d.keys():
			if type(d[key]) != type({}):
				
				output += "---> "*nest + '<b>' + str(key) + '</b>' + ': ' + str(d[key]) + '<br>'
			else:
				output += '<b>' + str(key) + '</b>'+ ':' + ppdict(d[key],nest + 1) + '<br>'
	except:
		output += str(d)
	return output

#define client functions
from bottle import route, run, static_file

@route('/')
def index():
	f = open('./report/system.templ','r')
	template = f.read()
	f.close()

	trigger = "-"*80 + '<br>'
	trigger += "Current Volitility Quartile: " + str(server.get_active_quartile()) + '<br>'
	trigger += "Buy Order Trigger* @ $"+"%.2f"%json.loads(server.get_target())['buy'] + '<br>' * 2
	trigger += "* Will report $0 if target is too far away from the current price.<br> bcbookie also uses additional logic to screen potential orders.<br>"
	trigger += "-"*80 + '<br>' * 2

	clients = "-"*80 + '<br>'
	gdhl = json.loads(server.get_gene_def_hash_list())
	clients += "Gene Library (" + str(len(gdhl))  + ')<br>'
	for gdh in gdhl:
		clients += "----> "+ gdh + '<br>'
	clients += "-"*80 + '<br>' * 2

	clients += "-"*80 + '<br>'
	pid_list = json.loads(server.pid_list(180))
	clients += "Active Clients (" + str(len(pid_list))  + ')<br>'
	for pid in pid_list:
		clients += "----> "+ pid + '<br>'
	clients += "-"*80 + '<br>' * 2

	pids = json.loads(server.get_pids())
	monitor = "-"*80 + '<br>'
	monitor += "Process monitor info (by PID)" + '<br>'
	monitor += "-"*80 + '<br>'
	monitor +=  ppdict(pids) + '<br>'*2
	monitor = monitor.replace('\n','<br>')

	best = "-"*80 + '<br>'
	best += "Highest scoring genes (per quartile)" + '<br>'
	best += "-"*80 + '<br>'
	for quartile in [1,2,3,4]:
		try:
			ag = json.loads(server.get(60*60*24,quartile))
		except:
			ag = {"Gene server didn't return a dictionary.":"Gene server didn't return a dictionary."}
		best += "-"*80 + '<br>'
		best += "Quartile: " + str(quartile) + " :: " + str(time.ctime()) + '<br>'
		best += ppdict(ag) + '<br>'
	best = best.replace('\n','<br>')
	template = template.replace('{LAST_UPDATE}',time.ctime())
	template = template.replace('{SYS_TRIGGER}',trigger)
	template = template.replace('{SYS_MONITOR}',monitor)
	template = template.replace('{SYS_CLIENTS}',clients)
	template = template.replace('{SYS_BEST_GENES}',best)
	return template


@route('/report/<filepath:path>')
def server_static(filepath):
	return static_file(filepath, root='./report')


run(host=ip_address, port=PORT)

print "http://" + ip_address + ":" + str(PORT)

