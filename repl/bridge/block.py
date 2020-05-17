from eudplib import *

class _BB_Metaclass(type):
    sigdict = {}
    def __init__(cls, name, bases, dct):
        super().__init__(name, bases, dct)

        if '_signature_' not in dct:
            raise RuntimeError("BridgeBlock should have its signature")

        signature = dct['_signature_']

        if type(cls).sigdict and (not isinstance(signature, bytes) or len(signature) != 4):
            print(bool(type(cls).sigdict))
            print(type(cls).sigdict)
            print(bool({}))
            print()
            raise RuntimeError("Signature should be bytes object with length 4")

        if signature in _BB_Metaclass.sigdict:
            raise RuntimeError("Signature duplicate - %s" % signature)

        _BB_Metaclass.sigdict[signature] = cls


class BridgeBlock(object, metaclass=_BB_Metaclass):
    '''
    Shared memory management class

    block structure
     * signature : 4 special bytes to identify block
     * size      : size of contents
     * contents  : user contents
    '''
    _signature_ = None

    def UpdateContent(self):
        '''
        Override the method, using EPD(self)
        '''
        buffer_epd = EPD(self)
        raise NotImplemented

    def GetBufferSize(self):
        '''
        Override the method
        '''
        raise NotImplemented

    def DynamicConstructed(self):
        return True

    def Evaluate(self):
        return GetObjectAddr(self) + 8

    def GetDataSize(self):
        return self.GetBufferSize() + 8

    def WritePayload(self, emitbuffer):
        buf_size = self.GetBufferSize()
        emitbuffer.WriteDword(type(self)._signature_)
        emitbuffer.WriteDword(buf_size)
        emitbuffer.WriteBytes(bytes(buf_size))
