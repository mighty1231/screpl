from eudplib.core.rawtrigger.strdict import DefUnitDict

def getDefaultUnitName(unitid):
    for name, _id in DefUnitDict.items():
        if _id == unitid:
            return name
    raise RuntimeError("Unknown unit, id=%d" % unitid)
