#ifndef LOGGERBLOCK_H
#define LOGGERBLOCK_H

#include "regionblock.h"

#define LOGGER_LINE_COUNT 500
#define LOGGER_LINE_SIZE 216

class LoggerBlock: public RegionBlock
{
    Q_OBJECT

public:
    LoggerBlock();

    int getSignature() override {
        return 0x42474f4c; // LOGB
    }

    void immediateProcess(void *block, int size) override;
    void afterProcess() override;

private:
    int log_index;
    char logger_log[LOGGER_LINE_COUNT][LOGGER_LINE_SIZE];

signals:
    void updateLoggerLog(QString);
};

#endif // LOGGERBLOCK_H
