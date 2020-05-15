from eudplib import *
from repl import (
    Application,
    AppCommand,
    argEncNumber,
    Array
)

from . import appManager

array = Array(10, [1, 2, 3])
ret = EUDVariable()

class ArrayTestApp(Application):
    def loop(self):
        if EUDIf()(appManager.keyPress("ESC")):
            appManager.requestDestruct()
            EUDReturn()
        EUDEndIf()
        appManager.requestUpdate()

    @AppCommand([argEncNumber, argEncNumber])
    def insert(self, i, value):
        array.insert(i, value)

    @AppCommand([argEncNumber])
    def delete(self, i):
        array.delete(i)

    @AppCommand([argEncNumber])
    def at(self, i):
        ret << array.at(i)

    @AppCommand([argEncNumber])
    def contains(self, i):
        ret << array.contains(i)

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
            writer.write_f("%D ", array)
        writer.write_f("\n")
        for i in range(10):
            writer.write_f("%D ", f_dwread_epd(contents + i))
        writer.write_f("\n")
        writer.write(0)
