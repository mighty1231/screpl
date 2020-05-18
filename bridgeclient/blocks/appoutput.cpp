#include "appoutput.h"

AppOutputBlock::AppOutputBlock()
{

}
void AppOutputBlock::immediateProcess(void *block, uint size)
{
    Q_ASSERT(size + sizeof(QObject) == sizeof(AppOutputBlock));
    memcpy(&this->app_output_size, block, size);

    // empty
    memset(block, 0, 4);
}

void AppOutputBlock::afterProcess()
{
    app_output[app_output_size] = 0;
    emit updateAppOutput(QString::fromUtf8(app_output));
}
