"""eudplib library for uuencode"""
from eudplib import *
from screpl.utils.byterw import REPLByteRW

reader = REPLByteRW()
writer = REPLByteRW()

@EUDFunc
def uuencode(src, srclength, target_epd):
    """encode src and store into target

    assert (length of target) >= upper(4/3 * srclength) + 1

    Args:
        src(EUDVariable): address of binary data
        scrlength(EUDVariable): size of src
        target_epd(EUDVariable): epd-address of encoded buffer, null-terminated
    """
    writer.seekepd(target_epd)
    reader.seekoffset(src)

    enc_byte = EUDVariable()
    status = EUDVariable()

    status << 0
    if EUDInfLoop()():
        EUDBreakIf(srclength == 0)

        byte = reader.read()

        if EUDIf()(status == 0):
            writer.write((byte//4)+32)
            DoActions(enc_byte.SetNumberX(byte*16, 0b110000))
            status << 1
        if EUDElseIf()(status == 1):
            DoActions(enc_byte.SetNumberX(byte//16, 0b1111))
            writer.write(enc_byte+32)
            DoActions(enc_byte.SetNumberX(byte*4, 0b111100))
            status << 2
        if EUDElse()():
            DoActions([
                enc_byte.SetNumberX(byte//64, 0b11),
                byte.SetNumberX(0, 0b11000000)])
            writer.write(enc_byte+32)
            writer.write(byte + 32)
            status << 0
        EUDEndIf()

        srclength -= 1
    EUDEndInfLoop()

    if EUDIf()(status == 1):
        DoActions(enc_byte.SetNumberX(0, 0b1111))
        writer.write(enc_byte+32)
    if EUDElseIf()(status == 2):
        DoActions(enc_byte.SetNumberX(0, 0b11))
        writer.write(enc_byte+32)
    EUDEndIf()
    writer.write(0)

@EUDFunc
def uudecode(buf, target_epd):
    """decode buf and store into target_epd

    assert (length of target) >= upper(3/4 * (length of buf before null))

    Args:
        buf(EUDVariable): address of uuencoded string.
        target_epd(EUDVariable): epd-address to store decoded binary data

    Rets:
        written(EUDVariable): size of decoded binary data
    """
    writer.seekepd(target_epd)
    reader.seekoffset(buf)

    dec8 = EUDVariable()
    status = EUDVariable()
    written = EUDVariable()

    status << 0
    written << 0
    if EUDInfLoop()():
        enc6 = reader.read()
        EUDBreakIf(enc6 == 0)

        enc6 -= 32
        if EUDIf()(status == 0):
            DoActions(dec8.SetNumberX(enc6*4, 0b11111100))
            status << 1
        if EUDElseIf()(status == 1):
            DoActions(dec8.SetNumberX(enc6//16, 0b00000011))
            writer.write(dec8)
            written += 1
            DoActions(dec8.SetNumberX(enc6*16, 0b11110000))
            status << 2
        if EUDElseIf()(status == 2):
            DoActions(dec8.SetNumberX(enc6//4, 0b00001111))
            writer.write(dec8)
            written += 1
            DoActions(dec8.SetNumberX(enc6*64, 0b11000000))
            status << 3
        if EUDElse()():
            DoActions(dec8.SetNumberX(enc6, 0b00111111))
            writer.write(dec8)
            written += 1
            status << 0
        EUDEndIf()
    EUDEndInfLoop()

    EUDReturn(written)

def test():
    from screpl.utils.debug import f_printf, DisplayWriter
    ret = Db(20)
    with DisplayWriter() as writer:
        uuencode(Db("Cat"), 3, EPD(ret))
        writer.write_f('uuencode(Db("Cat"), 3, EPD(ret)) %D\n',
                       f_memcmp(ret, Db("0V%T\0"), 5))
        uuencode(Db("Cat"), 2, EPD(ret))
        writer.write_f('uuencode(Db("Cat"), 2, EPD(ret)) %D\n',
                       f_memcmp(ret, Db("0V$\0"), 4))
        uuencode(Db("Cat"), 1, EPD(ret))
        writer.write_f('uuencode(Db("Cat"), 1, EPD(ret)) %D\n',
                       f_memcmp(ret, Db("0P\0"), 3))
        uuencode(Db("CatCa"), 5, EPD(ret))
        writer.write_f('uuencode(Db("CatCa"), 5, EPD(ret)) %D\n',
                       f_memcmp(ret, Db("0V%T0V$\0"), 8))
        written = uudecode(Db("0P\0"), EPD(ret))
        writer.write_f('uudecode(Db("0P\\0"), ret) ret=%D cmp=%D\n',
                       written, f_memcmp(ret, Db("Cat"), 1))
        written = uudecode(Db("0V$\0"), EPD(ret))
        writer.write_f('uudecode(Db("0V$\\0"), ret) ret=%D cmp=%D\n',
                       written, f_memcmp(ret, Db("Cat"), 2))
        written = uudecode(Db("0V%T\0"), EPD(ret))
        writer.write_f('uudecode(Db("0V%%T\\0"), ret) ret=%D cmp=%D\n',
                       written, f_memcmp(ret, Db("Cat"), 3))
        written = uudecode(Db("0V%T0V$\0"), EPD(ret))
        writer.write_f('uudecode(Db("0V%%T0V$\\0"), ret) ret=%D cmp=%D\n',
                       written, f_memcmp(ret, Db("CatCa"), 5))
        writer.write(0)