from eudplib import *

signature = [
    193, 250, 85, 96, 95, 202, 56, 94, 145, 228, 56, 67,
    8, 100, 106, 28, 96, 127, 190, 62, 186, 146, 132, 178,
    63, 45, 239, 182, 28, 238, 41, 164, 86, 71, 16, 251,
    123, 215, 182, 75, 92, 246, 174, 79, 228, 165, 193,
    209, 150, 25, 20, 75, 180, 123, 83, 126, 57, 232, 48,
    90, 89, 31, 7, 93, 7, 3, 26, 196, 255, 9, 228, 163,
    165, 153, 217, 129, 67, 234, 85, 33, 195, 245, 64,
    134, 13, 8, 238, 184, 71, 12, 60, 144, 176, 81, 68,
    239, 225, 45, 205, 148, 140, 1, 236, 132, 174, 43,
    98, 3, 179, 137, 192, 40, 48, 109, 14, 216, 244, 228,
    6, 21, 37, 177, 116, 15, 68, 39, 161, 110, 254, 31, 35,
    164, 205, 123, 167, 132, 103, 219, 165, 119, 154, 129,
    192, 18, 235, 192, 84, 162, 55, 30, 156, 198, 100, 36,
    100, 226, 51, 63, 113, 226
]
signature_start = b2i4(bytes(signature), 0)
content = bytes([f-1 for f in signature]) + \
        bytes(4 + 4 + 4 + 4 + 13 * 220 + 4 + 2000)

sharedRegion = Db(content)
sharedRegion_epd = EPD(sharedRegion)

noteFromExt = EPD(sharedRegion + 160)
noteToExt   = EPD(sharedRegion + 160 + 4)
frameCount  = EPD(sharedRegion + 160 + 4 + 4)
chatIndex   = EPD(sharedRegion + 160 + 4 + 4 + 4)
display     = EPD(sharedRegion + 160 + 4 + 4 + 4 + 4)


def comm_init():
    cp = f_getcurpl()
    f_setcurpl(sharedRegion_epd)
    DoActions([
        [SetDeaths(CurrentPlayer, Add, 0x01010101, 0),
         SetMemory(0x6509B0, Add, 1)] for _ in range(160)
    ])

    f_setcurpl(cp)

def comm_loop(frame_count):
    f_dwwrite_epd(noteToExt, 1)
    f_dwwrite_epd(frameCount, frame_count)
    f_dwwrite_epd(chatIndex, f_dwread_epd(EPD(0x640B58)))
    if EUDIf()(MemoryEPD(noteFromExt, Exactly, 0)):
        f_repmovsd_epd(display, EPD(0x640B60), (13*218+2)//4)
    EUDEndIf()
    f_dwwrite_epd(sharedRegion_epd, signature_start)
    f_dwwrite_epd(noteToExt, 0)
