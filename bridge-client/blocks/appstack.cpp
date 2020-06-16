#include "appstack.h"

AppStackBlock::AppStackBlock()
{

}

void AppStackBlock::immediateProcess(void *block, uint size)
{
    Q_ASSERT(size + sizeof(QObject) == sizeof(AppStackBlock));
    memcpy(&stack_size, block, size);
}

void AppStackBlock::afterProcess()
{
    QStringList app_names;

    char *namep = names;
    for (uint i=0; i<stack_size; i++) {
        app_names << QString::fromUtf8(namep);
        namep += strlen(namep) + 1;
    }

    emit updateAppStack(app_names);
}
