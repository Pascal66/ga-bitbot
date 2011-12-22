
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
	output = '<body bgcolor="#071C33"><font color="#757F8A">'
	output += '<b>ga-bitbot system monitor</b>' + '<br>'
	output += '<a href="./report/chart_test_zoom_1.html"> VIEW CHARTS </a>' + '<br>'
	pids = json.loads(server.get_pids())
	output += "-"*80 + '<br>'
	output += "Process monitor info (by PID)" + '<br>'
	output += "-"*80 + '<br>'
	output +=  ppdict(pids) + '<br>'*2

	output += "-"*80 + '<br>'
	output += "Highest scoring genes (per quartile)" + '<br>'
	output += "-"*80 + '<br>'
	for quartile in [1,2,3,4]:
		ag = json.loads(server.get(60*20,quartile))
		bobs = json.loads(server.get_bobs(quartile))			
		output += "-"*80 + '<br>'
		output += "Quartile: " + str(quartile) + " :: " + str(time.ctime()) + '<br>'
		output += ppdict(ag) + '<br>'
	output = output.replace('\n','<br>')
	return output


@route('/report/<filepath:path>')
def server_static(filepath):
	return static_file(filepath, root='./report')


run(host=ip_address, port=8090)

