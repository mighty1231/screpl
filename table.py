from eudplib import *
from command import EUDCommand
from utils import *
from encoder import ReadNumber, ReadName

tmpbuf = Db(150) # Temporarily store string

# global reference table
# list of (table_name, reference_table_pointer)
_table_list = []
_table_of_table = None

_var_list = []
_table_of_vars = None

_eudobj_vars = EUDStack(50)([0 for _ in range(50)])

def vartrace_init():
    global _var_list, _table_of_vars

    _table_of_vars = ReferenceTable([
        (name, var) for name, var in _var_list
    ])
    size = len(_var_list)

    @EUDCommand([])
    def cmd_vartrace():
        buf = EUDArray([EPD(Db(218)) for _ in range(size)])

        writer = EUDByteRW()

        i = EUDVariable()
        i << 0
        if EUDLoopN()(size):
            writer.seekepd(buf[i])
            writer.write_strepd(_table_of_vars.name[i])
            writer.write_strepd(EPD(makeText(' :   ')))
            writer.write_hex(_table_of_vars.value[i])
            writer.write(0)

            i += 1
        EUDEndLoopN()

        from board import Board
        br = Board.GetInstance()
        br.SetTitle(makeText('List of vars'))
        br.SetStaticContent(buf, size)
        br.SetMode(1)

    return cmd_vartrace


# init() should be called after all table is loaded
def table_init():
    global _table_list, _table_of_table

    # sort tables by name
    _table_of_table = ReferenceTable([
        (name, ptr) for name, ptr in _table_list
    ])
    size = len(_table_list)

    @EUDCommand([])
    def cmd_listTable():
        from board import Board
        br = Board.GetInstance()
        br.SetTitle(makeText('List of tables'))
        br.SetStaticContent(_table_of_table.name, size)
        br.SetMode(1)

    @EUDFunc
    def arg_EncodeTable(offset, delim, ref_offset_epd, retval_epd):
        if EUDIf()(ReadName(offset, delim, ref_offset_epd, EPD(tmpbuf)) == 1):
            idx, name_epd = EUDCreateVariables(2)
            DoActions([
                idx.SetNumber(0),
                # name_epd.SetNumber(EPD()),
            ])
            if EUDInfLoop()():
                EUDBreakIf(idx >= size)
                if EUDIf()(f_strcmp_epd(_table_of_table.name[idx], EPD(tmpbuf)) ==  0):
                    f_dwwrite_epd(retval_epd, _table_of_table.value[idx])
                    EUDReturn(1)
                EUDEndIf()
                DoActions([
                    idx.AddNumber(1),
                    name_epd.AddNumber(1)
                ])
            EUDEndInfLoop()
        EUDEndIf()
        f_dwwrite_epd(ref_offset_epd, offset)
        EUDReturn(0)

    @EUDCommand([arg_EncodeTable])
    def cmd_listTableContents(reftable_ptr):
        from board import Board

        f_simpleprint(reftable_ptr)
        f_print_memorytable(reftable_ptr)
        br = Board.GetInstance()
        br.SetContentsWithTable(
            makeText('Contents in Table'),
            reftable_ptr
        )
        br.SetMode(1)

    return cmd_listTable, cmd_listTableContents

class ReferenceTable(EUDStruct):
    _fields_ = [
        # name: EPD values of Db
        # val: Value of data. In general, decoded value
        #      Value becomes epd pointer of ReferenceTable on _global_table
        ('name', EUDArray),
        ('value', EUDArray),
        'size',
    ]

    def constructor(self, items, tbname = None):
        raise RuntimeError

    def constructor_static(self, items, tbname = None):
        names = [EPD(makeText(s[0])) for s in items]
        vals = [s[1] for s in items]

        self.name = EUDArray(names)
        self.value = EUDArray(vals)
        self.size = len(items)

        if tbname != None:
            global _table_list, _table_of_table
            assert _table_of_table == None, \
                    "All tables are should be declared before table_init()"
            _table_list.append((tbname, self))

    @EUDMethod
    def search(self, ptr, retval_epd):
        i = EUDVariable()
        i << 0
        if EUDInfLoop()():
            EUDBreakIf(i == self.size)
            if EUDIf()(f_strcmp_ptrepd(ptr, self.name[i]) == 0):
                f_dwwrite_epd(retval_epd, self.value[i])
                EUDReturn(1)
            EUDEndIf()
            i += 1
        EUDEndInfLoop()
        EUDReturn(0)

    @EUDMethod
    def print(self):
        i = EUDVariable()
        i << 0
        if EUDInfLoop()():
            EUDBreakIf(i == self.size)
            EUDBreakIf(i >= 4)
            f_dbepd_print(self.name[i])
            i += 1
        EUDEndInfLoop()
        EUDReturn(0)


