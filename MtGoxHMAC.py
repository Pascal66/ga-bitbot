
"""
MyGoxHMAC v0.01 

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

from contextlib import closing
from Crypto.Cipher import AES
import base64
import hmac
import hashlib
import time
import json
import urllib
import urllib2
import urlparse

class ServerError(Exception):
	def __init__(self, ret):
		self.ret = ret
	def __str__(self):
		return "Server error: %s" % self.ret
class UserError(Exception):
	def __init__(self, errmsg):
		self.errmsg = errmsg
	def __str__(self):
		return self.errmsg

class Client:
	def __init__(self, enc_password=""):
		if enc_password == "":
			print "MtGoxHMAC: Enter your API key file encryption password:"
			enc_password = raw_input()
		try:	
			f = open('./config/salt.txt','r')
			salt = f.read()
			f.close()
			hash_pass = hashlib.sha256(enc_password + salt).digest()

			f = open('./config/api_key.txt')
			ciphertext = f.read()
			f.close()
			decryptor = AES.new(hash_pass, AES.MODE_CBC)
			plaintext = decryptor.decrypt(ciphertext)
			d = json.loads(plaintext)
			self.key = d['key']
			self.secret = d['secret']
		except:
			print "\n\n\nError: you may have entered an invalid password or the encrypted api key file doesn't exist"
			print "If you haven't yet generated the encrypted key file, run the encrypt_api_key.py script."
			while 1:
				pass
		
		self.buff = ""
		self.timeout = 15
		self.__url_parts = urlparse.urlsplit("https://mtgox.com/api/0/")
		self.clock_window = time.time()
		self.clock = time.time()
		self.query_count = 0
		self.query_limit_per_time_slice = 5
		self.query_time_slice = 10

	def throttle(self):
		self.clock = time.time()
		tdelta = self.clock - self.clock_window
		if tdelta > self.query_time_slice:
			self.query_count = 0
			self.clock_window = time.time()
		self.query_count += 1
		if self.query_count > self.query_limit_per_time_slice:
			#throttle the connection
			#print "### Throttled ###"
			time.sleep(self.query_time_slice - tdelta)
		return
       
	def perform(self, path, params):
		self.throttle()
		nonce =  str(int(time.time()*1000))
		if params != None:
			params = params.items()
		else:
			params = []

		params += [(u'nonce',nonce)]
		post_data = urllib.urlencode(params)
		ahmac = base64.b64encode(str(hmac.new(base64.b64decode(self.secret),post_data,hashlib.sha512).digest()))

		# Create header for auth-requiring operations
		header = {
			"User-Agent": 'ga-bitbot',
			"Rest-Key": self.key,
			"Rest-Sign": ahmac
			}

		url = urlparse.urlunsplit((
			self.__url_parts.scheme,
			self.__url_parts.netloc,
			self.__url_parts.path + path,
			self.__url_parts.query,
			self.__url_parts.fragment
		))	
		
		req = urllib2.Request(url, post_data, header)

		with closing(urllib2.urlopen(req, post_data)) as res:
			data = json.load(res)

		if u"error" in data:
			if data[u"error"] == u"Not logged in.":
				raise UserError()
			else:
				raise ServerError(data[u"error"])
		else:
			return data
		

	def request(self, path, params):
		ret = self.perform(path, params)
		if "error" in ret:
			raise UserError(ret["error"])
		else:
			return ret

	#public api
	def get_info(self):
		return self.request('info.php', None) 
	def get_ticker(self):
		return self.request("ticker.php", None)["ticker"]  
	def get_depth(self):
		return self.request("data/getDepth.php", {"Currency":"USD"})
	def get_trades(self):
		return self.request("data/getTrades.php", None)
	def get_balance(self):
		return self.request("getFunds.php", None)
	def get_orders(self):
		return self.request("getOrders.php", None)

	def buy_btc(self, amount, price):
		if amount < 0.01:
			print "minimun amount is 0.1btc"
			return 0
		params = {"amount":str(amount), "price":str(price)}
		return self.request("buyBTC.php", params)


	def sell_btc(self, amount, price):
		if amount < 0.01:
			print "minimun amount is 0.1btc"
			return 0
		params = {"amount":str(amount), "price":str(price)}
		return self.request("sellBTC.php", params)
        
	def cancel_buy_order(self, oid):
		params = {"oid":str(oid), "type":str(2)}
		return self.request("cancelOrder.php", params)    

	def cancel_sell_order(self, oid):
		params = {"oid":str(oid), "type":str(1)}
		return self.request("cancelOrder.php", params)  


if __name__ == "__main__":
	def ppdict(d):
		#pretty print a dict
		print "-"*40
		for key in d.keys():
			print key,':',d[key]
		return d

	def pwdict(d,filename):
		#pretty write a dict
		f = open(filename,'w')
		for key in d.keys():
			f.write(key + " : " + str(d[key]) + "\n")
		f.write('\n' + '-'*80 + '\n')
		f.write(str(d))
		f.close()
		return d

	print "\nMTGoxHMAC module test"
	print "**warning: running this script will initiate then cancel an order on the MtGox exchange.**"

	print "\ndownloaded examples of the MtGox json format will be stored in the test_data folder."
	c = Client()
	b = ppdict(pwdict(c.buy_btc(1.5,0.25),'./test_data/mg_buy.txt'))
	s = ppdict(pwdict(c.sell_btc(1.0,100.00),'./test_data/mg_sell.txt'))
	ppdict(pwdict(c.get_info(),'./test_data/mg_info.txt'))
	ppdict(pwdict(c.get_ticker(),'./test_data/mg_ticker.txt'))
	ppdict(pwdict(c.get_depth(),'./test_data/mg_depth.txt'))
	ppdict(pwdict(c.get_balance(),'./test_data/mg_balance.txt'))	
	ppdict(pwdict(c.get_orders(),'./test_data/mg_orders.txt'))
	ppdict(pwdict(c.cancel_buy_order(b['oid']),'./test_data/mg_cancel_buy.txt'))
	ppdict(pwdict(c.cancel_sell_order(s['oid']),'./test_data/mg_cancel_sell.txt'))
	print "done."


