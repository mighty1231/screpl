#include "profile.h"

ProfileBlock::ProfileBlock()
{
    buf = 0;
    name_sent = false;
}

void ProfileBlock::immediateProcess(void *block, uint size)
{
    if (buf) {
        buf = new char[size];
        buf_size = size;
    } else {
        /* map has changed, initialize members */
        delete[] buf;
        buf = new char[buf_size];
        name_sent = false;
    }
    memcpy(buf, block, size);
}

void ProfileBlock::afterProcess()
{
    uint *ptr = (uint *) buf;
    uint count = *ptr;

    total_ms.clear();
    counter.clear();

    for (uint i=0; i<count; i++) {
        Q_ASSERT ((uint) ptr < (uint) buf + buf_size);
        uint offset = *ptr++;
        uint _total_ms = *ptr++;
        uint _counter = *ptr++;

        if (!name_sent) {
            Q_ASSERT (offset < buf_size);
            names.push_back(QString::fromUtf8(buf + offset, buf_size - offset));
        }
        total_ms.push_back(_total_ms);
        counter.push_back(_counter);
    }
    if (!name_sent) {
        emit updateProfileNames(names);
        name_sent = true;
    }

    emit updateProfile(total_ms, counter);
}
