#include "gametext.h"

GameTextBlock::GameTextBlock()
{

}
void GameTextBlock::immediateProcess(void *block, int size)
{
    Q_ASSERT(size == sizeof(GameTextBlock));
    memcpy(this, block, size);
}

void GameTextBlock::afterProcess()
{
    // display
    QString ret;
    int idx = displayIndex;
    for (int i=0; i<11; i++) {
        QString line = ignoreColor(display[idx]);
        ret.append(line);
        if (!line.endsWith('\n'))
            ret.append('\n');
        idx += 1;
        if (idx == 11)
            idx = 0;
    }
    ret.append("\n--------\n");
    ret.append(ignoreColor(display[12]));
    ret.append('\n');

    emit updateGameText(ret);
}
