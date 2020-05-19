#ifndef BLINDMODEDISPLAYBLOCK_H
#define BLINDMODEDISPLAYBLOCK_H

#include "regionblock.h"

#define DISPLAYBUFFER_SIZE 4000

class BlindModeDisplayBlock: public RegionBlock
{
    Q_OBJECT

public:
    BlindModeDisplayBlock();

    int getSignature() override {
        return 0x4e494c42; // BLIN
    }

    void immediateProcess(void *block, uint size) override;
    void afterProcess() override;

signals:
    void updateBlindModeDisplay(QString);

private:
    char buf[DISPLAYBUFFER_SIZE];
};

#endif // BLINDMODEDISPLAYBLOCK_H
