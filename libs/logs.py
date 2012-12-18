
"""
logs v0.01 

simple keyed dictionary log

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

import json

class logs:
	def __init__(self):
		self._log = {}
	
	def addkey(self,key):
		if self._log.has_key(key):
			return
		else:
			self._log.update({key:[]})
		return


	def append(self,key,value):
		if self._log.has_key(key):
			self._log[key].append(value)
		else:
			self._log.update({key:[value]})
		return

	def get(self,key):
		if self._log.has_key(key):
			return self._log[key]
		else:
			return None

	def reset(self):
		self._log = {}

	def json(self):
		return json.dumps(self._log)


if __name__ == "__main__":
	log = logs()
	log.append('alog',0)
	log.append('alog',1)
	log.append('alog',2)
	log.append('alog',3)
	log.append('alog',4)
	log.append('alog',5)

	log.append('blog','a')
	log.append('blog','b')
	log.append('blog','c')
	log.append('blog','d')
	log.append('blog','e')
	log.append('blog','f')

	log.append('list',[0,1,2])
	log.append('list',[3,4,5])
	log.append('list',[6,7,8])

	log.addkey('empty')

	print log.get('alog')
	print log.get('blog')
	print log.get('list')

	print log.json()
	log.reset()

	print log.get('alog')
	print log.get('blog')
	print log.get('list')

	
