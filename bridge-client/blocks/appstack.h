#ifndef APPSTACKBLOCK_H
#define APPSTACKBLOCK_H

#include "regionblock.h"

class AppStackBlock: public RegionBlock
{
    Q_OBJECT

public:
    AppStackBlock();

    int getSignature() override {
        return 0x54535041; // APST
    }

    void immediateProcess(void *block, uint size) override;
    void afterProcess() override;

signals:
    void updateAppStack(QStringList);

private:
    uint stack_size;
    char names[2000];
};

#endif // APPSTACKBLOCK_H
