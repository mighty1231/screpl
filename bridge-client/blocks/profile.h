#ifndef PROFILEBLOCK_H
#define PROFILEBLOCK_H

#include "regionblock.h"

class ProfileBlock: public RegionBlock
{
    Q_OBJECT

public:
    ProfileBlock();
    ~ProfileBlock() {
        if (buf)
            delete[] buf;
    }

    int getSignature() override {
        return 0x464f5250; // PROF
    }

    void immediateProcess(void *block, uint size) override;
    void afterProcess() override;

private:
    char *buf;
    uint buf_size;

    int count;
    QStringList prev_names;

signals:
    void updateProfileNames(QStringList names);
    void updateProfiles(QVector<uint> counter, QVector<uint> total_ms);
};

#endif // PROFILEBLOCK_H
