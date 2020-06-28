"""EffectApp

By modifying Scanner Sweep, show effect with various images, iscript and RLE.

.. codeblock:: C

    /* Raw Starcraft, Sprite380 Scanner Sweep Hit uses Image380 Scanner
     * Sweep Hit, and Image380 uses Iscript 253
     */
    spritesdat_ImageID[380] = v_imageid 
    imagesdat_IscriptID[v_imageid] = v_iscriptid
    imagesdat_RLE[v_imageid] = v_rle
"""

from eudplib import *

from screpl.core.appcommand import AppCommand
from screpl.core.application import Application
from screpl.encoder.const import ArgEncNumber
from screpl.resources.offset import (
    spritesdat_ImageID,
    imagesdat_IscriptID,
    imagesdat_RLE,
    unitsdat_ElevationLevel,
)
from screpl.resources.table.dat import (
    ISCRIPT_TABLE,
    IMAGE_TABLE,
    RLE_TABLE,
)
from screpl.utils.conststring import EPDConstString

from screpl.main import get_app_manager

from . import eval_screen_size

app_manager = get_app_manager()

VAL_DEFAULT = -1
v_imageid = EUDVariable(546)
v_iscriptid = EUDVariable(250)
v_rle = EUDVariable(VAL_DEFAULT)

DISPMODE_MAIN = 0
DISPMODE_MANUAL = 1
v_dispmode = EUDVariable(DISPMODE_MAIN)

POSMODE_SCREEN = 0
POSMODE_FIXED = 1
v_posmode = EUDVariable(POSMODE_SCREEN)
v_posx = EUDVariable()
v_posy = EUDVariable()

ISCRIPT_PREVIEW = 250

@EUDFunc
def create_effect(x, y, imageid, iscript, rle):
    """Create a Scanner Sweep Hit effect on point (x, y)"""
    le, te, re, be = [EPD(0x58DC60 + i*4) for i in range(4)]

    # backup location
    lv, tv, rv, bv = map(f_dwread_epd, [le, te, re, be])

    # adjust elevation level
    y += unitsdat_ElevationLevel.read(EncodeUnit("Scanner Sweep"))

    # modify image and iscript
    orig_im = spritesdat_ImageID.read(380) # Scanner Sweep Hit
    orig_is = imagesdat_IscriptID.read(imageid)
    orig_rle = imagesdat_RLE.read(imageid)
    spritesdat_ImageID.write(380, imageid)
    if EUDIfNot()(iscript == VAL_DEFAULT):
        imagesdat_IscriptID.write(imageid, iscript)
    EUDEndIf()
    if EUDIfNot()(rle == VAL_DEFAULT):
        imagesdat_RLE.write(imageid, rle)
    EUDEndIf()

    # make effect
    for ee, vv in zip([le, te, re, be], [x, y, x, y]):
        f_dwwrite_epd(ee, vv)
    DoActions([
        # make enable to create "Scanner Sweep"
        SetMemoryX(0x661558, SetTo, 1 << 17, 1 << 17),

        CreateUnit(1, "Scanner Sweep", 1, app_manager.su_id),
        RemoveUnit("Scanner Sweep", app_manager.su_id),
    ])

    # restore dat
    spritesdat_ImageID.write(380, orig_im)
    imagesdat_IscriptID.write(imageid, orig_is)
    imagesdat_RLE.write(imageid, orig_rle)

    # restore location
    for ee, vv in zip([le, te, re, be], [lv, tv, rv, bv]):
        f_dwwrite_epd(ee, vv)

@EUDFunc
def do_centerview():
    """Centerview to point (v_posx, v_posy)"""
    localid = f_getuserplayerid()
    if EUDIf()(localid == app_manager.su_id):
        EUDReturn()
    EUDEndIf()

    le, te, re, be = [EPD(0x58DC60 + i*4) for i in range(4)]
    origvals = []
    for ee in [le, te, re, be]:
        origvals.append(f_dwread_epd(ee))
    for ee, vv in zip([le, te, re, be], [v_posx, v_posy, v_posx, v_posy]):
        f_dwwrite_epd(ee, vv)
    f_setcurpl(localid)
    DoActions(CenterView(1))
    f_setcurpl2cpcache()

    # restore location
    for ee, vv in zip([le, te, re, be], origvals):
        f_dwwrite_epd(ee, vv)

@EUDFunc
def create_rle_table(imageid, iscriptid):
    """show rle original // 0, 6, 8, 10, 13, 16"""
    create_effect(v_posx-160, v_posy, imageid, iscriptid, -1)
    create_effect(v_posx-40, v_posy-40, imageid, iscriptid, 0)
    create_effect(v_posx+40, v_posy-40, imageid, iscriptid, 6)
    create_effect(v_posx+120, v_posy-40, imageid, iscriptid, 8)
    create_effect(v_posx-40, v_posy+40, imageid, iscriptid, 10)
    create_effect(v_posx+40, v_posy+40, imageid, iscriptid, 13)
    create_effect(v_posx+120, v_posy+40, imageid, iscriptid, 16)

class EffectApp(Application):
    def on_init(self):
        v_dispmode << DISPMODE_MAIN
        v_posmode << POSMODE_SCREEN

    def loop(self):
        global v_imageid, v_iscriptid, v_rle

        screen_size = eval_screen_size()
        v_centerx = f_dwread_epd(EPD(0x0062848C)) + (screen_size[0] // 2)
        v_centery = f_dwread_epd(EPD(0x006284A8)) + (screen_size[1] // 2)

        if EUDIf()(app_manager.key_press("ESC")):
            app_manager.request_destruct()
            EUDReturn()
        if EUDElseIf()(app_manager.key_down("F1")):
            v_dispmode << DISPMODE_MANUAL
            app_manager.request_update()
        if EUDElseIf()(app_manager.key_up("F1")):
            v_dispmode << DISPMODE_MAIN
            app_manager.request_update()
        if EUDElseIf()(app_manager.key_press("E", hold=["LCTRL"],
                                             sync=[v_centerx, v_centery])):
            if EUDIf()(v_posmode == POSMODE_FIXED):
                v_posmode << POSMODE_SCREEN
            if EUDElse()():
                v_posmode << POSMODE_FIXED
                v_posx << v_centerx
                v_posy << v_centery
            EUDEndIf()
            app_manager.request_update()
        if EUDElseIf()(app_manager.key_press("Q", sync=[v_centerx, v_centery])):
            # create single effect
            if EUDIf()(v_posmode == POSMODE_SCREEN):
                v_posx << v_centerx
                v_posy << v_centery
                do_centerview()
            EUDEndIf()
            create_effect(v_posx, v_posy, v_imageid, v_iscriptid, v_rle)
        if EUDElseIf()(app_manager.key_press("G", sync=[v_centerx, v_centery])):
            # create effect with various rle values
            if EUDIf()(v_posmode == POSMODE_SCREEN):
                v_posx << v_centerx
                v_posy << v_centery
                do_centerview()
            EUDEndIf()
            create_rle_table(v_imageid, v_iscriptid)
        if EUDElseIf()(app_manager.key_press("F7",
                                             sync=[v_centerx, v_centery])):
            if EUDIfNot()(v_imageid == 0):
                v_imageid -= 1

                # safe search - 560 circle marker causes crash
                RawTrigger(
                    conditions=v_imageid.Exactly(560),
                    actions=v_imageid.SetNumber(559))
                if EUDIf()(v_posmode == POSMODE_SCREEN):
                    v_posx << v_centerx
                    v_posy << v_centery
                    do_centerview()
                EUDEndIf()
                create_rle_table(v_imageid, ISCRIPT_PREVIEW)
                app_manager.request_update()
            EUDEndIf()
        if EUDElseIf()(app_manager.key_press("F8",
                                             sync=[v_centerx, v_centery])):
            if EUDIfNot()(v_imageid == 998):
                v_imageid += 1

                # safe search - 560 circle marker causes crash
                RawTrigger(
                    conditions=v_imageid.Exactly(560),
                    actions=v_imageid.SetNumber(561))
                if EUDIf()(v_posmode == POSMODE_SCREEN):
                    v_posx << v_centerx
                    v_posy << v_centery
                    do_centerview()
                EUDEndIf()
                create_rle_table(v_imageid, ISCRIPT_PREVIEW)
                app_manager.request_update()
            EUDEndIf()
        EUDEndIf()

    @AppCommand([ArgEncNumber])
    def im(self, imageid):
        v_imageid << imageid
        app_manager.request_update()

    @AppCommand([ArgEncNumber])
    def isc(self, iscriptid):
        v_iscriptid << iscriptid
        app_manager.request_update()

    @AppCommand([ArgEncNumber])
    def rle(self, rle):
        v_rle << rle
        app_manager.request_update()

    @AppCommand([])
    def d(self):
        v_iscriptid << -1
        v_rle << -1
        app_manager.request_update()

    def print(self, writer):
        if EUDIf()(v_dispmode == DISPMODE_MAIN):
            writer.write_f("Effect App. Press F1 to get manual\n")
            writer.write_f("Image: #%D %:constant;\n",
                v_imageid,
                (EPD(IMAGE_TABLE), v_imageid))

            if EUDIf()(v_iscriptid == -1):
                v_default_iscript = imagesdat_IscriptID.read(v_imageid)
                writer.write_f("Iscript: default(%D %:constant;)\n",
                    v_default_iscript,
                    (EPD(ISCRIPT_TABLE), v_default_iscript))
            if EUDElse()():
                writer.write_f("Iscript: #%D %:constant;\n",
                    v_iscriptid,
                    (EPD(ISCRIPT_TABLE), v_iscriptid))
            EUDEndIf()
            if EUDIf()(v_rle == -1):
                v_default_rle = imagesdat_RLE.read(v_imageid)
                writer.write_f("RLE: default(%D %:constant;)\n",
                    v_default_rle,
                    (EPD(RLE_TABLE), v_default_rle))
            if EUDElse()():
                writer.write_f("RLE: #%D %:constant;\n",
                    v_rle,
                    (EPD(RLE_TABLE), v_rle))
            EUDEndIf()
            writer.write_f("\nposition: %E (%D, %D)\n",
                EUDTernary(v_posmode==POSMODE_SCREEN)(
                    EPDConstString("SCREEN"))(
                    EPDConstString("FIXED")),
                v_posx, v_posy)

        if EUDElse()():
            writer.write_f(
                "Effect App creates effect with Scanner Sweep Hit\n"
                " 1. spritesdat_ImageID[380] <- v_imageid\n"
                " 2. imagesdat_IscriptID[v_imageid] <- v_iscriptid\n"
                " 3. imagesdat_RLE[v_imageid] <- v_rle\n"
                "Press Q/G to create effect with target RLE/various RLEs(default, 0, 6, 8, 10, 13, 16)\n"
                "Press CTRL+E to toggle position mode: SCREEN / FIXED\n"
                "Press F7 or F8 to change target image id\n"
                "Chat im(##), isc(##), and rle(##) to set target image id, iscript, and RLE, respectively\n"
                "Chat d() to set target iscript and RLE as default value\n"
                "Tip. iscript #250 is the shortest iscript that shows frame 0\n"
            )
        EUDEndIf()
        writer.write(0)
