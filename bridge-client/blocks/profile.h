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
    QVector<QString> names;
    QVector<uint> total_ms;
    QVector<uint> counter;

    bool name_sent;

signals:
    void updateProfileNames(QVector<QString> names);
    void updateProfile(QVector<uint> total_ms, QVector<uint> counter);
};

#endif // PROFILEBLOCK_H
