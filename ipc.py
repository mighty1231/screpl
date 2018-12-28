_fname = 'repl.key'
from eudplib import *

def generate_random_file():
	import random
	buf = []
	for i in range(128):
		buf.append(random.randrange(256))

	with open(_fname, 'wb') as f:
		f.write(bytes(buf))

def make_db():
	import binascii

	with open(_fname, 'rb') as f:
		data = binascii.hexlify(f.read())

	a = Db(len(data) + 4)
	acts = []
	for i in range(len(data)//4):
		acts.append(SetMemory(a+i*4, SetTo, b2i4(data[i*4:i*4+4])))
	acts.append(SetMemory(a+len(data), SetTo, a))
	DoActions(acts)
