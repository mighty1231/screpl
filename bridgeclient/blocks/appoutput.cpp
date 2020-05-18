#include "appoutput.h"

AppOutputBlock::AppOutputBlock()
{

}
void AppOutputBlock::immediateProcess(void *block, int size)
{
    Q_ASSERT(size == sizeof(AppOutputBlock));
    memcpy(this, block, size);
    ((AppOutputBlock *)block)->app_output_size= 0;
}

void AppOutputBlock::afterProcess()
{
    emit updateAppOutput(QString::fromUtf8(app_output));
}
