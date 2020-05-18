#ifndef APPOUTPUTBLOCK_H
#define APPOUTPUTBLOCK_H

#include "regionblock.h"

class AppOutputBlock : public RegionBlock
{
    Q_OBJECT

public:
    AppOutputBlock();

    int getSignature() override {
        return 0x54554f41; // AOUT
    }

    void immediateProcess(void *block, int size) override;
    void afterProcess() override;

signals:
    void updateAppOutput(QString);

private:
    int app_output_size;
    char app_output[2000];
};

#endif // APPOUTPUTBLOCK_H
