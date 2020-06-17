from eudplib import *

def ConstString(msg):
    if not hasattr(ConstString, 'textdict'):
        ConstString.textdict = {}
    textdict = ConstString.textdict
    if isinstance(msg, str):
        msg = msg.encode('utf-8')
    try:
        return textdict[msg]
    except KeyError:
        textdict[msg] = Db(msg + b'\0')
        return textdict[msg]

def EPDConstString(msg):
    return EPD(ConstString(msg))

def EPDConstStringArray(txt):
    lines = []
    if isinstance(txt, str):
        lines = txt.split('\n')
    elif isinstance(txt, list):
        for line in txt:
            lines += line.split('\n')
    ln = len(lines)
    return EUDArray([EPDConstString(line) for line in lines]), ln
