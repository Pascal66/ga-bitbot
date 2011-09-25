from Crypto.Cipher import AES
import hashlib
import json
import time
import random

print "\n\nga-bitbot API Key Encryptor v0.1a"
print "-" * 30
print "\n\n"

print "Enter the API KEY:"
key = raw_input()

print "\nEnter the API SECRET KEY:"
secret = raw_input()

print "\n\nEnter an encryption password:"
print "(This is the password ga-bitbot will require to execute trades)"
password = raw_input()


print "\n"
print "Generating the local password salt..."
pre_salt = str(time.time() * random.random() * 1000000) + 'H7gfJ8756Jg7HBJGtbnm856gnnblkjiINBMBV734'
salt = hashlib.sha512(pre_salt).digest()
f = open('./config/salt.txt','w')
f.write(salt)
f.close()


print "\n"
print "Generating the encrypted API KEY file..."
hash_pass = hashlib.sha256(password + salt).digest()
encryptor = AES.new(hash_pass, AES.MODE_CBC)
text = json.dumps({"key":key,"secret":secret})
#pad the text
pad_len = 16 - len(text)%16
text += " " * pad_len
ciphertext = encryptor.encrypt(text)
f = open('./config/api_key.txt','w')
f.write(ciphertext)
f.close()

print "Verifying encrypted file..."
f = open('./config/api_key.txt','r')
d = f.read()
f.close()
f = open('./config/salt.txt','r')
salt = f.read()
f.close()
hash_pass = hashlib.sha256(password + salt).digest()
decryptor = AES.new(hash_pass, AES.MODE_CBC)
text = decryptor.decrypt(d)
d = json.loads(text)
if d['key'] == key and d['secret'] == secret:
	print "Passed verification"
else:
	print "Failed verification...try again."

print "\nDon't forget your password:",password," This is what ga-bitbot will request to enable automated trading."
