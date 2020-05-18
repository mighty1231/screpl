from eudplib import *

class _BB_Metaclass(type):
    sigdict = {}
    def __init__(cls, name, bases, dct):
        super().__init__(name, bases, dct)

        if '_signature_' not in dct:
            raise RuntimeError("BridgeBlock should have its signature")

        signature = dct['_signature_']

        if type(cls).sigdict and (not isinstance(signature, bytes) or len(signature) != 4):
            raise RuntimeError("Signature should be bytes object with length 4")

        if signature in _BB_Metaclass.sigdict:
            raise RuntimeError("Signature duplicate - %s" % signature)

        _BB_Metaclass.sigdict[signature] = cls


class BridgeBlock(ConstExpr, metaclass=_BB_Metaclass):
    '''
    Shared memory management class

    block structure
     * signature : 4 special bytes to identify block
     * size      : size of contents
     * contents  : user contents
    '''
    _signature_ = None

    def __init__(self, region):
        super().__init__(self)
        self.region = region

    def UpdateContent(self):
        '''
        Override the method
        '''
        raise NotImplemented

    def GetBufferSize(self):
        '''
        Override the method
        '''
        raise NotImplemented

    def Evaluate(self):
        return self.region.GetBlockAddr(self) + 8

    def CollectDependency(self, emitbuffer):
        pass

    def WritePayload(self, emitbuffer):
        buf_size = self.GetBufferSize()
        emitbuffer.WriteDword(b2i4(type(self)._signature_))
        emitbuffer.WriteDword(buf_size)
        emitbuffer.WriteBytes(bytes(buf_size))
