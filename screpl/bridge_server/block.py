"""BridgeBlock class and its metaclass"""
from eudplib import ConstExpr, b2i4

class _BB_Metaclass(type):
    """Supporting class for BridgeBlock

    It manages :attribute:`BridgeBlock.signature` of BridgeBlock instances
    """
    sigdict = {}
    def __init__(cls, name, bases, dct):
        super().__init__(name, bases, dct)

        if 'signature' not in dct:
            raise RuntimeError(
                "BridgeBlock should define attribute 'signature'"
            )

        signature = dct['signature']
        if type(cls).sigdict and (not isinstance(signature, bytes)
                                  or len(signature) != 4):
            raise RuntimeError("Signature should be bytes with length 4")

        if signature in _BB_Metaclass.sigdict:
            raise RuntimeError("Signature duplicate - %s" % signature)

        _BB_Metaclass.sigdict[signature] = cls


class BridgeBlock(ConstExpr, metaclass=_BB_Metaclass):
    """Basic buffer management class used for shared memory

    BridgeBlock is abstract class to manage memory block that is shared
    with bridge client. It has following c structure:

    .. code-block:: C

        typedef struct _block {
            int32_t signature;
            int32_t block_size;
            char contents[]; // its size is equals to 'block_size'
        } block;
    """
    signature = b'brbl'

    def __init__(self, region):
        super().__init__(self)
        self.region = region

    def UpdateContent(self):
        """Updates contents of the block.

        Use `self` as a pointer to contents of the block.
        Required to be overrided.
        """
        raise NotImplementedError("Override UpdateContent")

    def GetBufferSize(self):
        """Returns size of its contents.

        Required to be overrided.
        """
        raise NotImplementedError("Override GetBufferSize")

    def Evaluate(self):
        """Magic method to address `self`

        It makes the block as a pointer to its contents.
        Override from :meth:`~eudplib.ConstExpr.Evaluate`.
        """
        return self.region.GetBlockAddr(self) + 8

    def CollectDependency(self, emitbuffer):
        """Override from :meth:`~eudplib.ConstExpr.CollectDependency`."""
        pass

    def WritePayload(self, emitbuffer):
        """Override from :meth:`~eudplib.ConstExpr.WritePayload`."""
        buf_size = self.GetBufferSize()
        emitbuffer.WriteDword(b2i4(type(self).signature))
        emitbuffer.WriteDword(buf_size)
        emitbuffer.WriteBytes(bytes(buf_size))
