#include "regionblock.h"


RegionBlock::RegionBlock()
{

}

QString RegionBlock::ignoreColor(const char *ptr)
{
    QByteArray ba;
    unsigned char c = *ptr;
    while (c != 0) {
        // string escape
        if (!(1 <= c && c <= 0x1F && c != '\t' && c != '\n') && c!=0x7F)
            ba.append(c);
        c = *(++ptr);
    }

    return QString::fromUtf8(ba);
}
