
"""
cache v0.01 

simple pickling cache wrapper for redis

Copyright 2012 Brian Monkaba

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

import cPickle
import sys

# DEBUG
#
sys.path.append('/usr/local/lib/python2.7/dist-packages/')

try:
	import redis
	using_redis = True
	print "cache: redis module detected"
except:
	redis = None
	using_redis = False


#simple pickling cache wrapper for redis
#if the optional redis server isn't being used, all functions return None
class cache:
	def __init__(self):
		self.using_redis = using_redis
		self.r = None
		if self.using_redis:
			try:
				self.r = redis.StrictRedis(host='127.0.0.1',port=6379,db=0)
			except:
				print "cache: can't connect to redis server, caching disabled"
				self.using_redis = False
			try:
				self.r.get('testing connection')
			except:
				print "cache: can't connect to redis server, caching disabled"
				self.using_redis = False


	def set(self,key,value):
		if self.using_redis:
			print "cache: set",key
			return self.r.set(key,cPickle.dumps(value))
		else:
			return None

	def get(self,key):
		if self.using_redis:
			print "cache: get",key
			value = self.r.get(key)
			if value == None:
				return None
			else:
				return cPickle.loads(value)
		else:
			return None

	def expire(self,key,expiration):
		if self.using_redis:
			print "cache: set expire",key
			return self.r.expire(key,expiration)
		return None

	def disable(self):
		print "cache: disabled"
		self.using_redis = False
		return


