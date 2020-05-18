#ifndef BRIDGEBLOCK_H
#define BRIDGEBLOCK_H

#include <QByteArray>
#include <QObject>


class RegionBlock: public QObject
{
    Q_OBJECT

public:
    RegionBlock();

    static QString ignoreColor(const char *);

    virtual int getSignature() = 0;
    virtual void immediateProcess(void *block, uint size) = 0;
    virtual void afterProcess() = 0;

};

#endif // BRIDGEBLOCK_H
