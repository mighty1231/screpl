import os

from eudplib import *

from screpl.utils.conststring import EPDConstString
from screpl.utils.debug import f_raise_error
from screpl.utils.referencetable import ReferenceTable

_DIRNAME = os.path.dirname(__file__)

def load_file(fname, size):
    with open(os.path.join(_DIRNAME, fname), 'rt') as f:
        data = f.read().strip().split('\n')
        assert len(data) == size, "size mismatch"

    table = ReferenceTable(
        [(name, i) for i, name in enumerate(data)],
        key_f=EPDConstString, final=True)

    return data, table

IMAGE, IMAGE_TABLE = load_file("data/Images.txt", 999)
ISCRIPT, ISCRIPT_TABLE = load_file("data/IscriptIDList.txt", 412)
RLE, RLE_TABLE = load_file("data/DrawList.txt", 18)

