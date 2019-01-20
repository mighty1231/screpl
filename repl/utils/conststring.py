from eudplib import *

def ConstString(msg):
	if not hasattr(ConstString, 'textdict'):
		ConstString.textdict = {}
	textdict = ConstString.textdict
	try:
		return textdict[msg]
	except KeyError:
		textdict[msg] = Db(u2b(msg) + b'\0')
		return textdict[msg]

def EPDConstString(msg):
	return EPD(ConstString(msg))

def EPDConstStringArray(txt):
	lines = []
	if type(txt) == str:
		lines = txt.split('\n')
	elif type(txt) == list:
		for line in txt:
			lines += line.split('\n')
	ln = len(lines)
	return EUDArray([EPDConstString(line) for line in lines]), ln
