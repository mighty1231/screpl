#include "blindmode.h"

BlindModeDisplayBlock::BlindModeDisplayBlock()
{

}

void BlindModeDisplayBlock::immediateProcess(void *block, int size)
{
    buf = new char[size];
    memcpy(buf, block, size);
    memset(block, 0, 4);
}

void BlindModeDisplayBlock::afterProcess()
{
    QString string = ignoreColor(buf);
    if (!string.isEmpty()) {
        emit updateBlindModeDisplay(string);
    }
    delete[] buf;
}
