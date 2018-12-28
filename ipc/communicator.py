from memorpy import MemWorker, Process

_fname = 'repl.key'

mw = MemWorker(name='StarCraft.exe')

import binascii

with open(_fname, 'rb') as f:
	data = binascii.hexlify(f.read())
addrs = [addr for addr in mw.mem_search(data)]

if len(addrs) != 1:
	raise RuntimeError

addr = addrs[0]
