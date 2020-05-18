#ifndef BLINDMODEDISPLAYBLOCK_H
#define BLINDMODEDISPLAYBLOCK_H

#include "regionblock.h"

class BlindModeDisplayBlock: public RegionBlock
{
    Q_OBJECT

public:
    BlindModeDisplayBlock();

    int getSignature() override {
        return 0x4e494c42; // BLIN
    }

    void immediateProcess(void *block, int size) override;
    void afterProcess() override;

signals:
    void updateBlindModeDisplay(QString);

private:
    char *buf;
};

#endif // BLINDMODEDISPLAYBLOCK_H
