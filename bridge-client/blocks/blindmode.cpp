#include "blindmode.h"

BlindModeDisplayBlock::BlindModeDisplayBlock()
{

}

void BlindModeDisplayBlock::immediateProcess(void *block, uint size)
{
    Q_ASSERT(size + sizeof(QObject) == sizeof(BlindModeDisplayBlock));
    memcpy(buf, block, size);
    memset(block, 0, 4);
}

void BlindModeDisplayBlock::afterProcess()
{
    QString string = ignoreColor(buf);
    if (!string.isEmpty()) {
        emit updateBlindModeDisplay(string);
    }
}
