#include "profile.h"

ProfileBlock::ProfileBlock() : buf(0), buf_size(0)
{

}

void ProfileBlock::immediateProcess(void *block, uint size)
{
    /* region has been changed */
    if (size != buf_size) {
        if (buf)
            delete[] buf;
        buf = new char[size];
        buf_size = size;
    }
    memcpy(buf, block, size);
}

void ProfileBlock::afterProcess()
{
    uint *ptr = (uint *) buf;
    uint count = *ptr++;

    QStringList names;
    QVector<uint> total_ms;
    QVector<uint> counter;

    for (uint i=0; i<count; i++) {
        Q_ASSERT ((uint) ptr < (uint) buf + buf_size);
        uint offset = *ptr++;
        uint _total_ms = *ptr++;
        uint _counter = *ptr++;

        Q_ASSERT (offset < buf_size);
        names << QString::fromUtf8(buf + offset);

        total_ms.push_back(_total_ms);
        counter.push_back(_counter);
    }

    if (prev_names.size() != names.size()) {
        emit updateProfileNames(names);
        prev_names = names;
    } else {
        bool hasChanged = false;
        for (int i=0; i<names.size(); i++) {
            if (names[i].compare(prev_names[i])) {
                hasChanged = true;
                break;
            }
        }
        if (hasChanged) {
            emit updateProfileNames(names);
            prev_names = names;
        }
    }

    emit updateProfiles(counter, total_ms);
}
