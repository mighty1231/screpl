#ifndef GAMETEXTBLOCK_H
#define GAMETEXTBLOCK_H

#include "regionblock.h"

class GameTextBlock: public RegionBlock
{
    Q_OBJECT

public:
    GameTextBlock();

    int getSignature() override {
        return 0x54584554; // TEXT
    }

    void immediateProcess(void *block, int size) override;
    void afterProcess() override;

signals:
    void updateGameText(QString);

private:
    int displayIndex;
    char display[13][218];
    char unused[2];
};

#endif // GAMETEXTBLOCK_H
