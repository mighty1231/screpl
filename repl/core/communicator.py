from eudplib import *

'''
struct SharedRegion {
    char signature[160];

    // Too much milk solution #3, busy-waiting by A
    int noteToSC;
    int noteFromSC;

    /* To SC */
    char command[300];

    /* From SC */
    int frameCount;

    int app_output_sz;
    char app_output[2000];

    int log_index;
    char logger_log[LOGGER_LINE_COUNT][LOGGER_LINE_SIZE];

    int displayIndex;
    char display[13][218];
    char _unused[2];
};
'''
LOGGER_LINE_SIZE = 216
LOGGER_LINE_COUNT = 500

members = [
    ('signature', 160),
    ('noteFromBridge', 4),
    ('noteToBridge', 4),
    ('command', 300),
    ('frameCount', 4),
    ('app_output_sz', 4),
    ('app_output', 2000),
    ('log_index', 4),
    ('logger_log', LOGGER_LINE_COUNT * LOGGER_LINE_SIZE),
    ('displayIndex', 4),
    ('display', 13*218),
    ('unused', 2)
]

# fill offsets
offsets = dict()
offset = 0
for key, sz in members:
    offsets[key] = offset
    offset += sz
region_size = offset

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
        bytes(region_size - len(signature))

shared_region = Db(content)

# relocate
for off in offsets:
    offsets[off] = shared_region + offsets[off]

# temporary storage
buf_command = Db(300)
app_output_sz = EUDVariable(0)
app_output = Db(2000)

def comm_init():
    cp = f_getcurpl()
    f_setcurpl(EPD(shared_region))
    DoActions([
        [SetDeaths(CurrentPlayer, Add, 0x01010101, 0),
         SetMemory(0x6509B0, Add, 1)] for _ in range(160 // 4)
    ])

    f_setcurpl(cp)

def comm_loop(manager):
    from ..apps.logger import buf_start_epd, next_epd_to_write, log_index
    prev_log_index = EUDVariable(0)

    # Too-much milk solution #3
    f_dwwrite_epd(EPD(offsets["noteToBridge"]), 1)
    if EUDIf()(Memory(offsets["noteFromBridge"], Exactly, 0)):
        # inside the if statement, make operations be minimalized
        f_dwwrite_epd(EPD(offsets["frameCount"]), manager.current_frame_number)

        ############# from bridge ###############
        # read command
        if EUDIfNot()(Memory(offsets["command"], Exactly, 0)):
            f_repmovsd_epd(EPD(buf_command), EPD(offsets["command"]), 300//4)
            DoActions(SetMemory(offsets["command"], SetTo, 0))
        EUDEndIf()

        ############## tp bridge ################
        # app output
        if EUDIf()(Memory(offsets["app_output_sz"], Exactly, 0)):
            f_repmovsd_epd(EPD(offsets["app_output"]), EPD(app_output), 2000//4)
            f_dwwrite_epd(EPD(offsets["app_output_sz"]), app_output_sz)
            app_output_sz << 0
        EUDEndIf()

        # logger log
        quot, rem = f_div(prev_log_index, LOGGER_LINE_COUNT)
        rel = rem * (LOGGER_LINE_SIZE // 4)
        if EUDInfLoop()():
            EUDBreakIf(prev_log_index == log_index)

            f_repmovsd_epd(
                EPD(offsets["logger_log"]) + rel,
                buf_start_epd + rel,
                LOGGER_LINE_SIZE // 4
            )

            DoActions([
                rel.AddNumber(LOGGER_LINE_SIZE // 4),
                rem.AddNumber(1),
                prev_log_index.AddNumber(1)
            ])
            Trigger(
                conditions=rem.Exactly(LOGGER_LINE_COUNT),
                actions=[
                    rem.SetNumber(0), rel.SetNumber(0)
                ]
            )
        EUDEndInfLoop()
        f_dwwrite_epd(EPD(offsets["log_index"]), log_index)

        # display
        f_dwwrite_epd(EPD(offsets["displayIndex"]), f_dwread_epd(EPD(0x640B58)))
        f_repmovsd_epd(EPD(offsets["display"]), EPD(0x640B60), (13*218+2)//4)
    EUDEndIf()
    f_dwwrite_epd(EPD(offsets["noteToBridge"]), 0)

    # keep signature (make bridge to know REPL is alive)
    f_dwwrite_epd(EPD(offsets["signature"]), signature_start)

    # command
    if EUDIfNot()(Memory(buf_command, Exactly, 0)):
        manager.current_app_instance.onChat(buf_command)
        DoActions(SetMemory(buf_command, SetTo, 0))
    EUDEndIf()
