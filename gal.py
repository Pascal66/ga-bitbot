
"""
gal v0.01 

ga-bitbot system launcher

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

__appversion__ = "0.01a"
print "ga-bitbot system launcher v%s"%__appversion__

WATCHDOG_TIMEOUT = 60 * 10 #seconds
MONITORED_PROCESS_LAUNCH_TIMEOUT = 20 #seconds

monitored_launch = ['pypy gts.py 1 n','pypy gts.py 2 n','pypy gts.py 3 n','pypy gts.py 4 n','pypy gts.py 1 y','pypy gts.py 2 y','pypy gts.py 3 y','pypy gts.py 4 y']
unmonitored_launch = ['python wc_server.py','pypy report_gen.py']

monitor = {}	#variables to track monitored/unmonitored processes
no_monitor = []

import atexit
import sys
from subprocess import check_output as call, Popen, PIPE
import shlex
from os import environ
import os
from time import *

#open a null file to redirect output from the subprocesses 
fnull = open(os.devnull,'w')

#update the dataset
print "Synching the local datafeed..."
Popen(shlex.split('python bcfeed_synch.py -d')).wait()

#launch the bcfeed script to collect data from the live feed
print "Starting the live datafeed capture script..."
p = Popen(shlex.split('python bcfeed.py'),stdin=fnull, stdout=fnull, stderr=fnull)
no_monitor.append(p)

print "Launching the xmlrpc server..."
Popen(shlex.split('pypy gene_server.py'),stdin=fnull, stdout=fnull, stderr=fnull)
sleep(1) #give the server time to start


# connect to the xml server
#
import gene_server_config
import xmlrpclib
import json
__server__ = gene_server_config.__server__
__port__ = str(gene_server_config.__port__)
server = xmlrpclib.Server('http://' + __server__ + ":" + __port__)  
print "Connected to",__server__,":",__port__

# create and register callback function to do a clean shutdown of the system on exit.
def shutdown():
	global monitor
	global no_monitor
	for p in no_monitor:
		p.terminate()
	for pid in monitor.keys():
		monitor[pid]['process'].terminate()
	sys.stderr = fnull
	server.shutdown()

atexit.register(shutdown)

a = ""
while not(a == 'y' or a == 'n'):
	print "Load archived gene database? (y/n)"
	a = raw_input()

if a == 'y':
	print "Loading the gene database..."
	print server.reload()

print "Launching GA Clients..."


#collect system process PIDS for monitoring. 
#(not the same as system OS PIDs -- They are more like GUIDs as this is a multiclient distributed system) 
epl = json.loads(server.pid_list()) #get the existing pid list

#start the monitored processes
for cmd_line in monitored_launch:
	p = Popen(shlex.split(cmd_line),stdin=fnull, stdout=fnull, stderr=fnull)
	retry = MONITORED_PROCESS_LAUNCH_TIMEOUT
	while retry > 0:
		sleep(1)
		cpl = json.loads(server.pid_list())	#get the current pid list
		npl = list(set(epl) ^ set(cpl)) 	#find the new pid(s)
		epl = cpl				#update the existing pid list
		if len(npl) > 0:
			monitor.update({npl[0]:{'cmd':cmd_line,'process':p}})	#store the pid/cmd_line/process
			print "Monitored Process Launched (PID:",npl[0],"CMD:",cmd_line,")"
			break
		else:
			retry -= 1
	if retry == 0:
		print "ERROR: Monitored Process Failed to Launch","(CMD:",cmd_line,")"

#start unmonitored processes
for cmd_line in unmonitored_launch:
	p = Popen(shlex.split(cmd_line),stdin=fnull, stdout=fnull, stderr=fnull)
	print "Unmonitored Process Launched (CMD:",cmd_line,")"
	no_monitor.append(p)	#store the popen instance
	sleep(1) #wait a while before starting the report_gen script


print "\nMonitoring Processes..."
while 1:
	#process monitor loop
	for pid in monitor.keys():
		sleep(5)
		if server.pid_check(pid,WATCHDOG_TIMEOUT) == "NOK":
			#watchdog timed out
			print "WATCHDOG: PID",pid,"EXPIRED"
			#remove the expired PID
			server.pid_remove(pid)
			epl = json.loads(server.pid_list()) 	#get the current pid list
			cmd_line = monitor[pid]['cmd']
			#terminate the process
			monitor[pid]['process'].terminate()
			monitor.pop(pid)
			#launch new process
			p = Popen(shlex.split(cmd_line),stdin=fnull, stdout=fnull, stderr=fnull)
			sleep(2)
			#store new PID
			cpl = json.loads(server.pid_list())	#get the current pid list
			npl = list(set(epl) ^ set(cpl)) 	#find the new pid(s)
			epl = cpl				#update the existing pid list
			monitor.update({npl[0]:{'cmd':cmd_line,'process':p}})	#store the pid/cmd_line/process
			print "Process Launched (PID:",npl[0],"CMD:",cmd_line,")"

	#periodicaly tell the server to save the gene db
	server.save()

fnull.close()
