from eudplib import *

from repl.core.application import Application
from repl.core.appcommand import AppCommand
from repl.encoder.const import ArgEncNumber
from repl.utils.array import REPLArray

from . import app_manager

array = REPLArray.construct(10, [1, 2, 3])
ret = EUDVariable()

class REPLArrayTestApp(Application):
    def loop(self):
        if EUDIf()(app_manager.keyPress("ESC")):
            app_manager.requestDestruct()
            EUDReturn()
        EUDEndIf()
        app_manager.requestUpdate()

    @AppCommand([ArgEncNumber])
    def append(self, value):
        array.append(value)

    @AppCommand([ArgEncNumber, ArgEncNumber])
    def insert(self, i, value):
        array.insert(i, value)

    @AppCommand([ArgEncNumber])
    def delete(self, i):
        array.delete(i)

    @AppCommand([ArgEncNumber])
    def at(self, i):
        ret << array.at(i)

    @AppCommand([ArgEncNumber])
    def contains(self, i):
        ret << array.contains(i)

    @AppCommand([])
    def pop(self):
        ret << array.pop()

    @AppCommand([])
    def sort(self):
        array.sort()

    def print(self, writer):
        max_size = array.max_size
        size     = array.size
        contents = array.contents
        end      = array.end
        writer.write_f("max_size %D sz %D ret %D\n",
            max_size,
            size,
            ret
        )
        for value in array.values():
            writer.write_f("%D ", value)
        writer.write_f("\n")
        for i in range(10):
            writer.write_f("%D ", f_dwread_epd(contents + i))
        writer.write_f("\n")

        # cast test
        arr2 = EUDVariable()
        arr2 << array

        arr3 = REPLArray(arr2)
        for value in arr3.values():
            writer.write_f("%D ", value)
        writer.write_f("\n")
        for i in range(10):
            writer.write_f("%D ", f_dwread_epd(arr3.contents + i))
        writer.write_f("\n")
        writer.write(0)
